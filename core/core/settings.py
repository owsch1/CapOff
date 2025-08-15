from pathlib import Path
import os
from datetime import timedelta


# --- Basis ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Sicherheit / Debug ---
SECRET_KEY = "django-insecure-^1m&p#aij9&b0nip6nga8%1@z-_9lgls55c7j+f89iq#a6)8g4"  # Lehrübung
DEBUG = True
ALLOWED_HOSTS = []  # im Unterricht oft leer lassen, in Prod z. B. ["127.0.0.1", "localhost"]

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
        "DIRS": [],   # optional: [BASE_DIR / "templates"]
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
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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

# --- DRF + JWT ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
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
STATICFILES_DIRS = [BASE_DIR / "static"]  # optional, falls Ordner existiert
STATIC_ROOT = BASE_DIR / "staticfiles"    # für collectstatic in Prod

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "Media"

# --- Sonstiges ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),     # Access Token 7 Tage gültig
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),   # Refresh Token 30 Tage gültig
    "ROTATE_REFRESH_TOKENS": False,                 # kein automatischer Refresh
    "BLACKLIST_AFTER_ROTATION": True,               # Logout = ungültig machen
    "AUTH_HEADER_TYPES": ("Bearer",),               # Bearer Token Header
}