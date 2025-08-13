from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)  # optional

    def __str__(self):
        return self.username