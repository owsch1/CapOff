from django.urls import path
from .views import RegisterAPIView, EmailTokenObtainPairView, MeAPIView, LogoutAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="auth_register"),
    path("auth/login/", EmailTokenObtainPairView.as_view(), name="auth_login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth_refresh"),
    path("auth/me/", MeAPIView.as_view(), name="auth_me"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth_logout"),
]