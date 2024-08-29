from django.urls import re_path

from .views import ReviewDeleteView, ReviewListView

urlpatterns = [
    re_path(r"^(?P<class_id>\d+)/?$", ReviewListView.as_view(), name="review-list"),
    re_path(
        r"^(?P<class_id>\d+)/delete/(?P<review_id>\d+)/?$",
        ReviewDeleteView.as_view(),
        name="review-delete",
    ),
]
