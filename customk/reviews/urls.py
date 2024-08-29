from django.urls import re_path

from .views import (
    PhotoReviewListView,
    ReviewImageListView,
    ReviewListView,
    ReviewUpdateView,
)

urlpatterns = [
    re_path(r"^(?P<class_id>\d+)/$", ReviewListView.as_view(), name="review-list"),
    re_path(
        r"^(?P<class_id>\d+)/update/(?P<review_id>\d+)/$",
        ReviewUpdateView.as_view(),
        name="review-update",
    ),
    re_path(
        r"^(?P<review_id>\d+)/images/$",
        ReviewImageListView.as_view(),
        name="review-image-list",
    ),
    re_path(
        r"^photo-reviews/$", PhotoReviewListView.as_view(), name="photo-review-list"
    ),
]
