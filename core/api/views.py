from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, F
from django.shortcuts import get_object_or_404

from .models import Product, Basket, Favorite, Banner, Brand
from .serializers import (
    ProductSerializer, ProductListSerializer,
    BasketSerializer, FavoriteSerializer,
    BannerSerializer, BrandSerializer
)
from .choices import BannerLocation


class HomeIndexAPIView(APIView):
    """
    Main:
      - head_banner (1x)
      - brands ()
      - bestsellers
      - discounts
    Limits via Query: ?brands=4&best=12&disc=12
    """
    permission_classes = [AllowAny]

    def get(self, request):
        b_lim  = int(request.query_params.get('brands', 4))
        bs_lim = int(request.query_params.get('best', 12))
        d_lim  = int(request.query_params.get('disc', 12))

        head_banner = Banner.objects.filter(is_active=True, location=BannerLocation.HEAD).order_by('-id')[:1]
        brands = Brand.objects.annotate(product_count=Count('products')).order_by('-product_count', 'title')[:b_lim]
        bestsellers = (Product.objects.filter(is_active=True)
                       .annotate(fav_count=Count('favorited_by'))
                       .order_by('-fav_count', '-created_at')[:bs_lim])
        discounts = (Product.objects.filter(is_active=True, old_price__isnull=False, new_price__lt=F('old_price'))
                     .annotate(discount_amount=F('old_price') - F('new_price'))
                     .order_by('-discount_amount', '-created_at')[:d_lim])

        return Response({
            "head_banner": BannerSerializer(head_banner, many=True, context={'request': request}).data,
            "brands":      BrandSerializer(brands, many=True, context={'request': request}).data,
            "bestsellers": ProductListSerializer(bestsellers, many=True, context={'request': request}).data,
            "discounts":   ProductListSerializer(discounts, many=True, context={'request': request}).data,
        }, status=status.HTTP_200_OK)

# ---------- PRODUCTS ----------

class ProductListCreateAPIView(APIView):
    """
    GET: aktive Produkte (optional ?category=, ?limit=)
    POST: Produkt anlegen
    """
    permission_classes = [AllowAny]

    def get(self, request):
        qs = (Product.objects
              .filter(is_active=True)
              .order_by('-created_at')
              .prefetch_related('brands'))

        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)

        try:
            limit = int(request.query_params.get('limit', 0))
        except (TypeError, ValueError):
            limit = 0
        if limit > 0:
            qs = qs[:limit]

        data = ProductListSerializer(qs, many=True, context={'request': request}).data
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                ProductSerializer(instance, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    """
    GET/PUT/PATCH/DELETE für einzelnes Produkt
    """
    permission_classes = [AllowAny]  # für PUT/DELETE ggf. IsAdminUser

    def get_object(self, pk):
        return get_object_or_404(Product.objects.prefetch_related('brands'), pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        return Response(
            ProductSerializer(product, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- FAVORITES ----------

class FavoriteListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fav_qs = Favorite.objects.filter(user=request.user).select_related('product')
        product_ids = list(fav_qs.values_list('product_id', flat=True))
        products = [f.product for f in fav_qs]
        return Response({
            'product_ids': product_ids,
            'products': ProductSerializer(products, many=True, context={'request': request}).data
        }, status=status.HTTP_200_OK)


class FavoriteToggleAPIView(APIView):
    """
    POST   /api/favorites/<product_id>/        -> add
    DELETE /api/favorites/<product_id>/remove/ -> remove
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
        ser = FavoriteSerializer(fav)
        return Response(ser.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, product_id):
        fav = Favorite.objects.filter(user=request.user, product_id=product_id).first()
        if not fav:
            return Response({'detail': 'Favorite not found'}, status=status.HTTP_404_NOT_FOUND)
        fav.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- BASKET ----------

class BasketAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_or_create_basket(self, user):
        return Basket.objects.get_or_create(user=user)[0]

    def get(self, request):
        basket = self._get_or_create_basket(request.user)
        return Response(BasketSerializer(basket).data, status=status.HTTP_200_OK)

    def post(self, request):
        basket = self._get_or_create_basket(request.user)
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, pk=product_id)
        basket.products.add(product)
        return Response({'detail': 'Added to basket'}, status=status.HTTP_200_OK)

    def delete(self, request):
        basket = self._get_or_create_basket(request.user)
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, pk=product_id)
        basket.products.remove(product)
        return Response({'detail': 'Removed from basket'}, status=status.HTTP_200_OK)


# ---------- HOMEPAGE BLOCS (Choices genutzt) ----------

class HomeHeadBannerAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Banner.objects.filter(is_active=True, location=BannerLocation.HEAD).order_by('-id')[:1]
        return Response(BannerSerializer(qs, many=True, context={'request': request}).data)


class HomeMiddleBannersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 10))
        except (TypeError, ValueError):
            limit = 10
        qs = Banner.objects.filter(is_active=True, location=BannerLocation.MIDDLE).order_by('-id')[:limit]
        return Response(BannerSerializer(qs, many=True, context={'request': request}).data)


class HomeCatalogBannersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 10))
        except (TypeError, ValueError):
            limit = 10
        qs = Banner.objects.filter(is_active=True, location=BannerLocation.CATALOG).order_by('-id')[:limit]
        return Response(BannerSerializer(qs, many=True, context={'request': request}).data)


class PopularBrandsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 4))
        except (TypeError, ValueError):
            limit = 4
        qs = (Brand.objects
              .annotate(product_count=Count('products'))
              .order_by('-product_count', 'title')[:limit])
        return Response(BrandSerializer(qs, many=True, context={'request': request}).data)


class BestsellerProductsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 12))
        except (TypeError, ValueError):
            limit = 12
        qs = (Product.objects.filter(is_active=True)
              .annotate(fav_count=Count('favorited_by'))
              .order_by('-fav_count', '-created_at')[:limit])
        return Response(ProductListSerializer(qs, many=True, context={'request': request}).data)


class DiscountedProductsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 12))
        except (TypeError, ValueError):
            limit = 12
        qs = (Product.objects.filter(is_active=True, old_price__isnull=False)
              .filter(new_price__lt=F('old_price'))
              .annotate(discount_amount=F('old_price') - F('new_price'))
              .order_by('-discount_amount', '-created_at')[:limit])
        return Response(ProductListSerializer(qs, many=True, context={'request': request}).data)




