from django.urls import re_path

from questions.views import QuestionListView, AllQuestionsListView

urlpatterns = [
    re_path(r"^$", AllQuestionsListView.as_view(), name="all-questions"),
    re_path(
        r"^(?P<class_id>\d+)/?$", QuestionListView.as_view(), name="class-question-list"
    ),
]
