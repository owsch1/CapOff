from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Product(models.Model):
    image = models.ImageField(
        upload_to='products/%Y/%m/',  # media/products/Jahr/Monat
        blank=True,
        null=True
    )
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)  # einfacher Text
    old_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Basket(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='baskets'
    )
    products = models.ManyToManyField(
        Product, blank=True, related_name='in_baskets'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Basket #{self.pk} of {self.user}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Verhindert doppelte Likes

    def __str__(self):
        return f'{self.user} likes {self.product}'