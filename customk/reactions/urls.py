from django.urls import re_path

from .views import ReactToReviewView

urlpatterns = [
    re_path(
        r"^(?P<class_id>\d+)/?$", ReactToReviewView.as_view(), name="react-to-review"
    ),
]
