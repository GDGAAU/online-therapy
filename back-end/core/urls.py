"""
core/urls.py
=============
Root URL configuration.

API versioning is handled via URL prefix:
  /api/v1/...

Interactive docs:
  /api/schema/          → OpenAPI JSON
  /api/docs/            → Swagger UI
  /api/redoc/           → ReDoc
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from djoser.views import UserViewSet
from account.views import LogoutView, GoogleLoginView
urlpatterns = [
  # Admin
  path("admin/", admin.site.urls),

  # Auth (Djoser + JWT)
  path(
      "api/v1/auth/register/",
      UserViewSet.as_view({"post": "create"}),
      name="auth-register",
  ),
  path("api/v1/auth/logout/", LogoutView.as_view(), name="auth-logout"),
  path("api/v1/auth/google/", GoogleLoginView.as_view(), name="google-login"),
  path("api/v1/auth/", include("djoser.urls")),
  path("api/v1/auth/", include("djoser.urls.jwt")),
  # API v1
  path("api/v1/therapy/", include("therapy.urls")),
  path("api/v1/articles/", include("blog.urls")),
  path("api/v1/ai/", include("ai.urls")),

  # OpenAPI / Docs
  path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
  path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
  path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
