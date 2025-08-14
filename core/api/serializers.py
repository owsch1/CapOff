from rest_framework import serializers
from .models import Product, Basket, Favorite, Brand, Banner


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'title', 'logo']


class ProductSerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True, read_only=True)
    has_discount = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'image', 'title', 'category',
            'old_price', 'new_price', 'description',
            'created_at', 'is_active',
            'brands', 'has_discount', 'discount_amount',
        ]

    def get_has_discount(self, obj):
        return obj.old_price is not None and obj.new_price < obj.old_price

    def get_discount_amount(self, obj):
        if obj.old_price is not None and obj.new_price < obj.old_price:
            return obj.old_price - obj.new_price
        return None


class ProductListSerializer(ProductSerializer):
    is_favorite = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['is_favorite']

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return obj.favorited_by.filter(user=user).exists()


class BasketSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Basket
        fields = ['id', 'user', 'products', 'created_at']
        read_only_fields = ['id', 'created_at', 'user', 'products']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'description', 'cover', 'location', 'is_active', 'created_at']