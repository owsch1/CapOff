from django.db.models import Count, F
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Product, Basket, BasketItem, Favorite, Banner, Brand,
    ProductImage, Storage, Size, Order
)
from .serializers import (
    ProductSerializer, ProductListSerializer, ProductDetailSerializer,
    BasketSerializer, FavoriteSerializer,
    BannerSerializer, BrandSerializer,
    OrderSerializer, OrderDetailSerializer
)
from .filters import ProductFilter
from .choices import BannerLocation


# ---------- HOMEPAGE INDEX ----------
class HomeIndexAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        b_lim = int(request.query_params.get('brands', 4))
        bs_lim = int(request.query_params.get('best', 12))
        d_lim = int(request.query_params.get('disc', 12))

        head_banner = Banner.objects.filter(
            is_active=True, location=BannerLocation.HEAD
        ).order_by('-id')[:1]

        brands = (Brand.objects
                  .annotate(product_count=Count('products'))
                  .order_by('-product_count', 'title')[:b_lim])

        bestsellers = (Product.objects.filter(is_active=True)
                       .annotate(fav_count=Count('favorited_by'))
                       .order_by('-fav_count', '-created_at')[:bs_lim])

        discounts = (Product.objects.filter(
                        is_active=True,
                        old_price__isnull=False,
                        new_price__lt=F('old_price'))
                     .annotate(discount_amount=F('old_price') - F('new_price'))
                     .order_by('-discount_amount', '-created_at')[:d_lim])

        return Response({
            "head_banner": BannerSerializer(head_banner, many=True, context={'request': request}).data,
            "brands": BrandSerializer(brands, many=True, context={'request': request}).data,
            "bestsellers": ProductListSerializer(bestsellers, many=True, context={'request': request}).data,
            "discounts": ProductListSerializer(discounts, many=True, context={'request': request}).data,
        }, status=status.HTTP_200_OK)


# ---------- PRODUCTS ----------
class ProductListCreateAPIView(generics.ListCreateAPIView):
    """
    Produktliste mit Filtermöglichkeiten (Preis, Kategorie, Brand, Aktiv-Status).
    GET: gefilterte Liste
    POST: neues Produkt anlegen
    """
    queryset = Product.objects.filter(is_active=True).prefetch_related("brands", "images", "stocks")
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    permission_classes = [AllowAny]


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Einzelnes Produkt abrufen, ändern oder löschen.
    """
    queryset = Product.objects.filter(is_active=True).prefetch_related("brands", "images", "stocks__size")
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]


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
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
        ser = FavoriteSerializer(fav, context={'request': request})
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
        basket, _ = Basket.objects.get_or_create(user=user)
        return basket

    def get(self, request):
        basket = self._get_or_create_basket(request.user)
        return Response(BasketSerializer(basket, context={'request': request}).data, status=status.HTTP_200_OK)

    def post(self, request):
        basket = self._get_or_create_basket(request.user)
        product_id = request.data.get('product_id')
        size_id = request.data.get('size_id')
        qty = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'detail': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, pk=product_id)

        size = get_object_or_404(Size, pk=size_id) if size_id else None
        item, created = BasketItem.objects.get_or_create(
            basket=basket, product=product, size=size,
            defaults={'quantity': qty}
        )
        if not created:
            item.quantity += qty
            item.save()

        return Response({'detail': 'Added to basket'}, status=status.HTTP_200_OK)

    def delete(self, request):
        basket = self._get_or_create_basket(request.user)
        product_id = request.data.get('product_id')
        size_id = request.data.get('size_id')

        if not product_id:
            return Response({'detail': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)

        qs = BasketItem.objects.filter(basket=basket, product_id=product_id)
        if size_id:
            qs = qs.filter(size_id=size_id)

        deleted, _ = qs.delete()
        if not deleted:
            return Response({'detail': 'Item not found in basket'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'detail': 'Removed from basket'}, status=status.HTTP_200_OK)


# ---------- ORDERS ----------
class OrderListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: Liste aller Bestellungen des Users
    POST: Neue Bestellung aus dem aktuellen Warenkorb erzeugen
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (self.request.user.orders
                .prefetch_related("items__product", "items__size")
                .order_by("-created_at"))

    def perform_create(self, serializer):
        basket = Basket.objects.filter(user=self.request.user).prefetch_related("items").first()
        if not basket or not basket.items.exists():
            raise ValidationError("Basket is empty")

        order = serializer.save(user=self.request.user)

        for item in basket.items.all():
            stock = Storage.objects.filter(product=item.product, size=item.size).first()
            if stock and stock.quantity < item.quantity:
                raise ValidationError(f"Nicht genug Bestand für {item.product}")
            if stock:
                stock.quantity -= item.quantity
                stock.save()

            order.items.create(
                product=item.product,
                size=item.size,
                quantity=item.quantity,
                price=item.product.new_price,
            )

        basket.items.all().delete()
        return order


class OrderDetailAPIView(generics.RetrieveAPIView):
    """
    Detailansicht einer Bestellung inkl. Positionen.
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (self.request.user.orders
                .prefetch_related("items__product", "items__size"))


# ---------- HOMEPAGE BLOCS ----------
class HomeHeadBannerAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Banner.objects.filter(is_active=True, location=BannerLocation.HEAD).order_by('-id')[:1]
        return Response(BannerSerializer(qs, many=True, context={'request': request}).data)


class HomeMiddleBannersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10) or 10)
        qs = Banner.objects.filter(is_active=True, location=BannerLocation.MIDDLE).order_by('-id')[:limit]
        return Response(BannerSerializer(qs, many=True, context={'request': request}).data)


class HomeCatalogBannersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10) or 10)
        qs = Banner.objects.filter(is_active=True, location=BannerLocation.CATALOG).order_by('-id')[:limit]
        return Response(BannerSerializer(qs, many=True, context={'request': request}).data)


class PopularBrandsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 4) or 4)
        qs = (Brand.objects.annotate(product_count=Count('products'))
              .order_by('-product_count', 'title')[:limit])
        return Response(BrandSerializer(qs, many=True, context={'request': request}).data)


class BestsellerProductsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 12) or 12)
        qs = (Product.objects.filter(is_active=True)
              .annotate(fav_count=Count('favorited_by'))
              .order_by('-fav_count', '-created_at')[:limit])
        return Response(ProductListSerializer(qs, many=True, context={'request': request}).data)


class DiscountedProductsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 12) or 12)
        qs = (Product.objects.filter(is_active=True, old_price__isnull=False, new_price__lt=F('old_price'))
              .annotate(discount_amount=F('old_price') - F('new_price'))
              .order_by('-discount_amount', '-created_at')[:limit])
        return Response(ProductListSerializer(qs, many=True, context={'request': request}).data)