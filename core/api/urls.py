from django.urls import path
from .views import (
    product_list, product_detail,
    favorite_list, favorite_add, favorite_remove,
    basket_view
)

urlpatterns = [
    # Produkte
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', product_detail, name='product-detail'),

    # Favoriten
    path('favorites/', favorite_list, name='favorite-list'),
    path('favorites/<int:product_id>/', favorite_add, name='favorite-add'),              # POST
    path('favorites/<int:product_id>/remove/', favorite_remove, name='favorite-remove'), # DELETE

    # Basket
    path('basket/', basket_view, name='basket'),
]