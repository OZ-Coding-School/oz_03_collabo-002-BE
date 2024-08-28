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

    answer = models.TextField(null=True, blank=True)
    answer_title = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Question by {self.user_id.name} on {self.class_id.title}"
