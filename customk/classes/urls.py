from django.urls import re_path

from classes.views import ClassListView

urlpatterns = [
    re_path(r"^$", ClassListView.as_view(), name="class-list"),
]
