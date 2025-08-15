from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .models import User


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    model = User

    list_display = ("id", "email", "username", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "date_joined")
    search_fields = ("email", "username", "phone_number")
    ordering = ("-date_joined",)

    fieldsets = (
        ("Login-Daten", {"fields": ("email", "password")}),
        ("Persönliche Daten", {"fields": ("username", "phone_number", "avatar", "address")}),
        ("Berechtigungen", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Zeiten", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "is_staff", "is_superuser", "is_active"),
        }),
    )