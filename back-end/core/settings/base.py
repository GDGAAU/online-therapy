"""
Django Settings - Base Configuration
====================================
Shared settings used across all environments.
Environment-specific overrides live in:
  - core/settings/development.py
  - core/settings/production.py
"""

from pathlib import Path
import os
from urllib.parse import urlparse
import dj_database_url
from dotenv import load_dotenv
import cloudinary

load_dotenv()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
)

# ─── Paths ──────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# ─── Security ───────────────────────────────────────────────
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure-default-for-dev-only")
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
NOTIFICATIONS_ENABLED = True
REMINDER_HOURS_BEFORE = 24

# ─── Application Definition ─────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "djoser",
    "corsheaders",
    "drf_spectacular",
    "anymail",
    "cloudinary_storage",
    "cloudinary",
]

LOCAL_APPS = [
    "account.apps.AccountConfig",
    "admin_app.apps.AdminAppConfig",
    "therapy.apps.TherapyConfig",
    "blog.apps.BlogConfig",
    "ai.apps.AiConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── Middleware ─────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",           # Must be before CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.RequestLoggingMiddleware",        # Custom debug middleware
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# ─── Templates ──────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ─── Database ───────────────────────────────────────────────
_db_url = os.environ.get("DATABASE_URL", "")
if _db_url:
    DATABASES = {"default": dj_database_url.parse(_db_url, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST'),
            'PORT': os.environ.get('POSTGRES_PORT'),
        }
    }

# ─── Auth ───────────────────────────────────────────────────
AUTH_USER_MODEL = "account.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Internationalization ────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─── Static / Media ─────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Cloudinary settings
_cloudinary_url = os.environ.get('CLOUDINARY_URL')
if not _cloudinary_url:
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    if cloud_name and api_key and api_secret:
        _cloudinary_url = f"cloudinary://{api_key}:{api_secret}@{cloud_name}"

CLOUDINARY_STORAGE = {
    'CLOUDINARY_URL': _cloudinary_url
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Throttle rate configuration ─────────────────────────────
AUTH_RATE_THROTTLE_RATE = os.environ.get("AUTH_RATE_THROTTLE_RATE", "5/minute")
REGISTER_RATE_THROTTLE_RATE = os.environ.get("REGISTER_RATE_THROTTLE_RATE", "3/hour")
PASSWORD_RESET_RATE_THROTTLE_RATE = os.environ.get("PASSWORD_RESET_RATE_THROTTLE_RATE", "3/hour")

# ─── DRF ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "auth": AUTH_RATE_THROTTLE_RATE,
        "register": REGISTER_RATE_THROTTLE_RATE,
        "password_reset": PASSWORD_RESET_RATE_THROTTLE_RATE,
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# ─── JWT ────────────────────────────────────────────────────
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 15))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 7))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "CHECK_USER_IS_ACTIVE": True,
}

# ─── Djoser ───────────────────────────────────────────────
DJOSER = {
    "LOGIN_FIELD": "email",
    "USER_ID_FIELD": "id",
    "SEND_ACTIVATION_EMAIL": True,
    "USER_CREATE_PASSWORD_RETYPE": True,
    "ACTIVATION_URL": "verify-email/{uid}/{token}",
    "PASSWORD_RESET_CONFIRM_URL": "reset-password/{uid}/{token}",
    "DOMAIN": urlparse(os.environ.get("PUBLIC_APP_URL", "http://localhost:5173")).netloc
    or os.environ.get("PUBLIC_APP_URL", "localhost:5173"),
    "SERIALIZERS": {
        "user_create": "account.serializers.UserCreateSerializer",
        "user": "account.serializers.UserSerializer",
        "current_user": "account.serializers.UserSerializer",
    },
    "VIEWS": {
        "user_create": "account.views.CustomUserViewSet"
    },
    "EMAIL": {
        "activation": "account.email.CustomActivationEmail",
        "password_reset": "account.email.CustomPasswordResetEmail",
    },
}

# ─── CORS ───────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")
CORS_ALLOW_CREDENTIALS = True

# ─── API Documentation ───────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "Online Therapy API",
    "DESCRIPTION": "RESTful API for the Online Therapy platform. Handles auth, appointments, therapist management, and notifications.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {"name": "auth", "description": "Authentication endpoints"},
        {"name": "users", "description": "User profile management"},
        {"name": "appointments", "description": "Appointment booking & management"},
        {"name": "therapists", "description": "Therapist directory"},
    ],
}

# ─── Google OAuth ────────────────────────────────────────────
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()

# ─── Email ──────────────────────────────────────────────────
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
ANYMAIL = {
    "SENDGRID_API_KEY": SENDGRID_API_KEY,
}
EMAIL_BACKEND = (
    "anymail.backends.sendgrid.EmailBackend"
    if SENDGRID_API_KEY
    else "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_FROM", os.environ.get("DEFAULT_FROM_EMAIL", "noreply@onlinetherapy.com"))

# Frontend URL (for email links)
FRONTEND_URL = os.environ.get("PUBLIC_APP_URL", "http://localhost:5173")

# ─── Sites ──────────────────────────────────────────────────
SITE_ID = 1

# ─── Sentry ─────────────────────────────────────────────────
SENTRY_DSN = os.environ.get("SENTRY_DSN_BACKEND", "")
