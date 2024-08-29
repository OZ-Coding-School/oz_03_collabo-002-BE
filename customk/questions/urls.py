from django.urls import re_path

from questions.views import QuestionListView

urlpatterns = [
    re_path(
        r"^(?P<class_id>\d+)/?$", QuestionListView.as_view(), name="class-question-list"
    )
]
