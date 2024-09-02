from django.urls import re_path

from .views import FavoriteView

urlpatterns = [
    re_path(r"^$", FavoriteView.as_view(), name="favorite"),
]
