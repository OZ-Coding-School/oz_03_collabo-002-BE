from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import path
from django.urls.conf import include


def hello_test(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello World")


urlpatterns = [
    path("", hello_test, name="hello_test"),
    path("admin/", admin.site.urls),
    path("api/v1/classes/", include("classes.urls")),
    path("api/v1/question/", include("questions.urls")),
    path("api/v1/reviews/", include("reviews.urls")),
]
