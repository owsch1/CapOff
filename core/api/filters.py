import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.NumberFilter(field_name="category__id")
    brand = django_filters.NumberFilter(field_name="brands__id")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Product
        fields = ["min_price", "max_price", "category", "brand", "is_active"]