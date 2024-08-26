from django.urls import path

from .views import AnswerListView, QuestionListView

urlpatterns = [
    path("<int:class_id>/", QuestionListView.as_view(), name="class-question-list"),
    path("<int:class_id>/answer/", AnswerListView.as_view(), name="class-answer-list"),
]
