from django.db import models
from classes.models import Class
from users.models import User
from common.models import CommonModel


class Question(CommonModel):
    # TODO 로그인 기능 구현 시 user model null 삭제
    course = models.ForeignKey(Class, related_name="questions", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField(blank=False)
    question_title = models.TextField(blank=False)

    def __str__(self):
        return f"Question by {self.user.username} on {self.course.title}"


class Answer(CommonModel):
    # TODO 문의답변 작성에 대한 권한 설정
    # TODO 로그인 기능 구현 시 user model null 삭제
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.TextField()
    answer_title = models.TextField(null=True, blank=True)
