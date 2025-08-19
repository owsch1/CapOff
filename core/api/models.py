from django.db import models
from django.contrib.auth import get_user_model
from .choices import BannerLocation

User = get_user_model()


class Brand(models.Model):
    title = models.CharField(max_length=120, unique=True, db_index=True)
    logo = models.ImageField(upload_to='brands/%Y/%m/', blank=True, null=True)

    def __str__(self):
        return self.title


class Size(models.Model):
    """S, M, L, XL ... frei erweiterbar."""
    title = models.CharField(max_length=16, unique=True, db_index=True)
    order = models.PositiveIntegerField(default=0)  # zur Sortierung (S<M<L<XL)

    class Meta:
        ordering = ("order", "title")

    def __str__(self):
        return self.title


class Product(models.Model):
    image = models.ImageField(upload_to='products/%Y/%m/', blank=True, null=True)  # Hauptbild
    title = models.CharField(max_length=200, db_index=True)
    category = models.CharField(max_length=100, db_index=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    brands = models.ManyToManyField(Brand, blank=True, related_name='products')

    def __str__(self):
        return self.title

    @property
    def has_discount(self):
        return self.old_price is not None and self.new_price < self.old_price


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

    def __str__(self):
        return f"{self.product} • {self.size} • qty={self.quantity}"


class Basket(models.Model):
    """Warenkorb des Users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Basket #{self.pk} of {self.user}'


class BasketItem(models.Model):
    """Produkte im Warenkorb inkl. Größe & Menge."""
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='basket_items')
    size = models.ForeignKey(Size, on_delete=models.PROTECT, null=True, blank=True, related_name='basket_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('basket', 'product', 'size')
        indexes = [models.Index(fields=['basket', 'product', 'size'])]

    def __str__(self):
        s = f" • {self.size}" if self.size_id else ""
        return f"BasketItem({self.product}{s} x{self.quantity})"


class Favorite(models.Model):
    """Favoritenliste der User."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        indexes = [models.Index(fields=['user', 'product'])]

    def __str__(self):
        return f'{self.user} likes {self.product}'


class Banner(models.Model):
    """Werbebanner an verschiedenen Positionen."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='banners/%Y/%m/', blank=True, null=True)
    location = models.CharField(
        max_length=20,
        choices=BannerLocation.CHOICES,
        default=BannerLocation.HEAD,
        db_index=True
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} [{self.location}]'


# -------------------------
# ✅ Bestell-Logik ergänzt
# -------------------------

class Order(models.Model):
    """Bestellung eines Users."""
    STATUS_CHOICES = [
        ("pending", "Offen"),
        ("paid", "Bezahlt"),
        ("shipped", "Versendet"),
        ("completed", "Abgeschlossen"),
        ("cancelled", "Storniert"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.pk} by {self.user} ({self.status})"


class OrderItem(models.Model):
    """Produkte innerhalb einer Bestellung."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    size = models.ForeignKey(Size, on_delete=models.PROTECT, null=True, blank=True, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Preis beim Kauf (nicht live aus Product!)

    def __str__(self):
        return f"{self.product} x{self.quantity} (Order {self.order_id})"