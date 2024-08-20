from django.urls import path

from classes.views import ClassListView

urlpatterns = [
    path("", ClassListView.as_view(), name="class-list"),

]
