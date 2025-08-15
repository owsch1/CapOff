# api/models.py
from django.db import models
from django.contrib.auth import get_user_model
from .choices import BannerLocation

User = get_user_model()


class Brand(models.Model):
    title = models.CharField(max_length=120, unique=True, db_index=True)
    logo = models.ImageField(upload_to='brands/%Y/%m/', blank=True, null=True)
    def __str__(self): return self.title


class Size(models.Model):
    """S, M, L, XL ... frei erweiterbar."""
    title = models.CharField(max_length=16, unique=True, db_index=True)
    order = models.PositiveIntegerField(default=0)  # zur Sortierung (S<M<L<XL)
    class Meta:
        ordering = ("order", "title")
    def __str__(self): return self.title


class Product(models.Model):
    image = models.ImageField(upload_to='products/%Y/%m/', blank=True, null=True)  # Hauptbild (optional)
    title = models.CharField(max_length=200, db_index=True)
    category = models.CharField(max_length=100, db_index=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    brands = models.ManyToManyField(Brand, blank=True, related_name='products')

    def __str__(self): return self.title
    @property
    def has_discount(self): return self.old_price is not None and self.new_price < self.old_price


class ProductImage(models.Model):
    """Zusätzliche Bilder fürs Carousel."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/%Y/%m/")
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ("order", "id")


class Storage(models.Model):
    """Lagerbestand pro Produkt/Größe."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="stocks")
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "size")
        indexes = [models.Index(fields=["product", "size"])]

    def __str__(self): return f"{self.product} • {self.size} • qty={self.quantity}"


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets')
    products = models.ManyToManyField(Product, blank=True, related_name='in_baskets')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'Basket #{self.pk} of {self.user}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'product')
        indexes = [models.Index(fields=['user', 'product'])]
    def __str__(self): return f'{self.user} likes {self.product}'


class Banner(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='banners/%Y/%m/', blank=True, null=True)
    location = models.CharField(max_length=20, choices=BannerLocation.CHOICES,
                                default=BannerLocation.HEAD, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.title} [{self.location}]'