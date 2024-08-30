from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^v1/schema/?$", SpectacularAPIView.as_view(), name="schema"),
    re_path(
        r"^v1/schema/swagger-ui/?$",
        permission_classes([AllowAny])(
            SpectacularSwaggerView.as_view(url_name="schema")
        ),
        name="swagger-ui",
    ),
    re_path(
        r"^v1/schema/redoc/?$",
        permission_classes([AllowAny])(SpectacularRedocView.as_view(url_name="schema")),
        name="redoc",
    ),
    re_path(r"^v1/users/?", include("users.urls")),
    re_path(r"^v1/classes/?", include("classes.urls")),
    re_path(r"^v1/question/?", include("questions.urls")),
    re_path(r"^v1/reviews/?", include("reviews.urls")),
]
