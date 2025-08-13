
from django.contrib import admin
from .models import Product, Basket, Favorite

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'new_price', 'old_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    filter_horizontal = ('products',)
    search_fields = ('user__username',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'created_at')
    search_fields = ('user__username', 'product__title')