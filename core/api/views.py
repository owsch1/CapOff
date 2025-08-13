from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Product, Basket, Favorite
from .serializers import (
    ProductSerializer, ProductListSerializer,
    BasketSerializer, FavoriteSerializer
)

# --------- PRODUCTS ---------

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def product_list(request):
    if request.method == 'GET':
        qs = Product.objects.filter(is_active=True).order_by('-created_at')

        # category=Caps
        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)

        data = ProductListSerializer(qs, many=True, context={'request': request}).data
        return Response(data, status=status.HTTP_200_OK)

    # POST
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([AllowAny])  # PUT/DELETE ggf. absichern (IsAuthenticated/IsAdminUser)
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        data = ProductSerializer(product, context={'request': request}).data
        return Response(data, status=status.HTTP_200_OK)

    if request.method == 'PUT':

        serializer = ProductSerializer(product, data=request.data)  # partial=False (Default)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# --------- FAVORITES ---------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorite_list(request):
    fav_qs = Favorite.objects.filter(user=request.user).select_related('product')
    product_ids = list(fav_qs.values_list('product_id', flat=True))
    products = [f.product for f in fav_qs]
    return Response({
        'product_ids': product_ids,
        'products': ProductSerializer(products, many=True, context={'request': request}).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def favorite_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    ser = FavoriteSerializer(fav)
    return Response(ser.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def favorite_remove(request, product_id):
    fav = Favorite.objects.filter(user=request.user, product_id=product_id).first()
    if not fav:
        return Response({'detail': 'Favorite not found'}, status=status.HTTP_404_NOT_FOUND)
    fav.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# --------- BASKET ---------

def _get_or_create_basket(user):
    return Basket.objects.get_or_create(user=user)[0]

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def basket_view(request):

    basket = _get_or_create_basket(request.user)

    if request.method == 'GET':
        return Response(BasketSerializer(basket).data, status=status.HTTP_200_OK)

    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'detail': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)

    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        basket.products.add(product)
        return Response({'detail': 'Added to basket'}, status=status.HTTP_200_OK)

    # DELETE
    basket.products.remove(product)
    return Response({'detail': 'Removed from basket'}, status=status.HTTP_200_OK)