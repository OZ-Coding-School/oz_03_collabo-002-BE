from django.urls import re_path
from .views import FavoriteView, FavoriteDeleteView

urlpatterns = [
    re_path(r"^$", FavoriteView.as_view(), name="favorite"),
    re_path(r"^(?P<favorite_id>\d+)/?$", FavoriteDeleteView.as_view(), name="favorite_detail"),
]
