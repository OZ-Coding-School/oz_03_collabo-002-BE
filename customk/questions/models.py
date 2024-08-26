from django.db import models

from classes.models import Class
from common.models import CommonModel
from users.models import User


class Question(CommonModel):
    class_id = models.ForeignKey(
        Class, related_name="questions", on_delete=models.CASCADE
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField(blank=False)
    question_title = models.TextField(blank=False)

    def __str__(self) -> str:
        return f"Question by {self.user_id.name} on {self.class_id.title}"


class Answer(CommonModel):
    question_id = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.TextField()
    answer_title = models.TextField(null=True, blank=True)
