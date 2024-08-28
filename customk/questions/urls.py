from django.urls import path

from questions.views import QuestionListView

urlpatterns = [
    path("<int:class_id>/", QuestionListView.as_view(), name="class-question-list")
]
