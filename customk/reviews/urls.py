from django.urls import path
from .views import ReviewListView

urlpatterns = [
    path('/<int:class_id>/', ReviewListView.as_view(), name='review-list-create'),
    path('/<int:class_id>/delete/<int:review_id>/', ReviewListView.as_view(), name='review-list-delete')
]
