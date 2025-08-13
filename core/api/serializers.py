from rest_framework import serializers
from .models import Product, Basket, Favorite

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'image', 'title', 'category',
            'old_price', 'new_price', 'description',
            'created_at', 'is_active'
        ]


class ProductListSerializer(ProductSerializer):
    # zusätzliches Flag für die Startseite
    is_favorite = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        # jetzt ist es eine Liste – kann sicher erweitert werden
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