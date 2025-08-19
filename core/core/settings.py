from pathlib import Path
from datetime import timedelta

# --- Basis ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Sicherheit / Debug ---
SECRET_KEY = "django-insecure-^1m&p#aij9&b0nip6nga8%1@z-_9lgls55c7j+f89iq#a6)8g4"  # nur für Dev
DEBUG = True
ALLOWED_HOSTS = []  # z. B. ["127.0.0.1", "localhost"] in Dev ok

# --- Apps ---
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Drittanbieter
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",  # <— wichtig für deine Filter

    # Projekt-Apps
    "api",
    "user",  # Custom User Model
]

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # z. B. [BASE_DIR / "templates"]
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# --- Datenbank ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mydatabase",
        "USER": "myuser",
        "PASSWORD": "admin1234",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# --- Passwortrichtlinien ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Custom User Model ---
AUTH_USER_MODEL = "user.User"

# --- DRF + Filter + JWT ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    # optional, damit du nicht in jeder View den Filter-Backend setzen musst:
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),     # Access Token 7 Tage
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),   # Refresh Token 30 Tage
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ALGORITHM": "HS256",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "UPDATE_LAST_LOGIN": True,
}

# --- Internationalisierung ---
LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True

# --- Static/Media ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # ← Ordner anlegen: <projekt>/static
STATIC_ROOT = BASE_DIR / "staticfiles"    # für collectstatic (Prod)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "Media"           # wenn Ordner so heißt, lassen; sonst "media"

# --- Sonstiges ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"