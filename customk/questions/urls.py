from django.urls import path, re_path

from questions.views import AllQuestionsListView, QuestionListView

urlpatterns = [
    re_path(r"^$", AllQuestionsListView.as_view(), name="all-questions"),
    re_path(
        r"^(?P<class_id>\d+)/?$", QuestionListView.as_view(), name="class-question-list"
    ),
]
