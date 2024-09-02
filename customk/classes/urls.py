from django.urls import re_path

from classes.views import ClassListView, ClassDetailView

urlpatterns = [
    re_path(r"^$", ClassListView.as_view(), name="class-list"),
    re_path(r"^(?P<id>\d+)/$", ClassDetailView.as_view(), name="class-detail"),
]
