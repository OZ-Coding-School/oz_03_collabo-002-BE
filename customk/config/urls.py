from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/schema", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/schema/swagger-ui/",
        permission_classes([AllowAny])(
            SpectacularSwaggerView.as_view(url_name="schema")
        ),
        name="swagger-ui",
    ),
    path(
        "api/v1/schema/redoc/",
        permission_classes([AllowAny])(SpectacularRedocView.as_view(url_name="schema")),
        name="redoc",
    ),
    path("api/v1/users/", include("users.urls")),
]
