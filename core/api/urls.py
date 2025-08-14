from django.urls import path
from .views import (
    # Products
    ProductListCreateAPIView, ProductDetailAPIView,
    # Favorites
    FavoriteListAPIView, FavoriteToggleAPIView,
    # Basket
    BasketAPIView,
    # Home blocks
    HomeHeadBannerAPIView, HomeMiddleBannersAPIView, HomeCatalogBannersAPIView,
    PopularBrandsAPIView, BestsellerProductsAPIView, DiscountedProductsAPIView,
    # Home index (kompakt)
    HomeIndexAPIView,
)

urlpatterns = [
    # Produkte
    path('products/', ProductListCreateAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),

    # Favoriten
    path('favorites/', FavoriteListAPIView.as_view(), name='favorite-list'),
    path('favorites/<int:product_id>/', FavoriteToggleAPIView.as_view(), name='favorite-add'),
    path('favorites/<int:product_id>/remove/', FavoriteToggleAPIView.as_view(), name='favorite-remove'),

    # Basket
    path('basket/', BasketAPIView.as_view(), name='basket'),

    # Homepage-Blöcke (einzeln)
    path('home/banner-head/', HomeHeadBannerAPIView.as_view(), name='home-banner-head'),
    path('home/banner-middle/', HomeMiddleBannersAPIView.as_view(), name='home-banner-middle'),
    path('home/banner-catalog/', HomeCatalogBannersAPIView.as_view(), name='home-banner-catalog'),
    path('home/popular-brands/', PopularBrandsAPIView.as_view(), name='home-popular-brands'),
    path('home/bestsellers/', BestsellerProductsAPIView.as_view(), name='home-bestsellers'),
    path('home/discounts/', DiscountedProductsAPIView.as_view(), name='home-discounts'),

    # Home-Index (alles in einem Endpoint)
    path('home/index/', HomeIndexAPIView.as_view(), name='home-index'),
]
