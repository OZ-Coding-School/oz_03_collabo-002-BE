from django.urls import re_path

from questions.views import AllQuestionsListView, QuestionListView

from django.urls import path
from .views import unanswered_questions_count

urlpatterns = [
    re_path(r"^$", AllQuestionsListView.as_view(), name="all-questions"),
    re_path(
        r"^(?P<class_id>\d+)/?$", QuestionListView.as_view(), name="class-question-list"
    ),
    path('admin/api/unanswered_questions_count/', unanswered_questions_count, name='unanswered_questions_count'),
]
