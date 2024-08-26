from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

def hello_test(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello World")


urlpatterns = [
    path("", hello_test, name="hello_test"),
    path("admin/", admin.site.urls),
    path("api/v1/classes/", include("classes.urls")),
    path("api/v1/question/", include("questions.urls")),
    path("api/v1/reviews/", include("reviews.urls")),
    path("api/v1/schema", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/v1/users/", include("users.urls")),
]
