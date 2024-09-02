from django.urls import re_path

from classes.views import ClassDetailView, ClassListView

urlpatterns = [
    re_path(r"^$", ClassListView.as_view(), name="class-list"),
    re_path(r"^(?P<class_id>\d+)/$", ClassDetailView.as_view(), name="class-detail"),
]
