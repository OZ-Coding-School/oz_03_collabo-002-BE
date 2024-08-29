from django.urls import path

from .views import (
    PhotoReviewListView,
    ReviewImageListView,
    ReviewListView,
    ReviewUpdateView,
)

urlpatterns = [
    path("<int:class_id>/", ReviewListView.as_view(), name="review-list"),
    path(
        "<int:class_id>/update/<int:review_id>/",
        ReviewUpdateView.as_view(),
        name="review-update",
    ),
    path(
        "<int:review_id>/images/",
        ReviewImageListView.as_view(),
        name="review-image-list",
    ),
    path("photo-reviews/", PhotoReviewListView.as_view(), name="photo-review-list"),
]
