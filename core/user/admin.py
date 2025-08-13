from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Extra', {'fields': ('avatar', 'address')}),
    )
    list_display = ('id', 'username', 'email', 'address', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'address')