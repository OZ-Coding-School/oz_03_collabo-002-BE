from django.urls import path

from questions.views.answer import AnswerListView
from questions.views.question import QuestionListView

urlpatterns = [
    path("<int:class_id>/", QuestionListView.as_view(), name="class-question-list"),
    path("<int:class_id>/answer/", AnswerListView.as_view(), name="class-answer-list"),
]
