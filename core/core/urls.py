from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API-Routen für verschiedene Apps
    path('api/', include('api.urls')),         # z. B. Menü / Produkte
    path('api/user/', include('user.urls')),   # z. B. Registrierung / Login
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)