# api/serializers.py
from rest_framework import serializers
from .models import (
    Product, Basket, Favorite, Brand, Banner,
    ProductImage, Size, Storage
)

# --- Brands ---
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'title', 'logo']

# --- Product images (Galerie) ---
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "order"]

# --- Product base ---
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

# --- Product list ---
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

# --- Product detail (Galerie + Größen + ähnliche) ---
class ProductDetailSerializer(ProductSerializer):
    gallery = ProductImageSerializer(source="images", many=True, read_only=True)
    sizes = serializers.SerializerMethodField()
    similar = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["gallery", "sizes", "similar"]

    def get_sizes(self, obj):
        result = {}
        sizes = Size.objects.all().order_by("order", "title")  # falls es 'order' gibt
        stock_map = {s.size_id: s.quantity for s in Storage.objects.filter(product=obj)}
        for size in sizes:
            qty = stock_map.get(size.id, 0)
            result[size.title] = {"available": qty > 0, "quantity": qty}
        return result

    def get_similar(self, obj):
        request = self.context.get("request")
        limit = 8
        if request:
            try:
                q = request.query_params.get("similar")
                if q:
                    limit = max(1, int(q))
            except Exception:
                pass
        qs = (Product.objects.filter(is_active=True, category=obj.category)
              .exclude(pk=obj.pk)
              .order_by('-created_at')
              .prefetch_related("brands"))[:limit]
        return ProductListSerializer(qs, many=True, context=self.context).data

# --- Basket ---
class BasketSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Basket
        fields = ['id', 'user', 'products', 'created_at']
        read_only_fields = ['id', 'created_at', 'user', 'products']

# --- Favorite ---
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

# --- Banners ---
class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'description', 'cover', 'location', 'is_active', 'created_at']