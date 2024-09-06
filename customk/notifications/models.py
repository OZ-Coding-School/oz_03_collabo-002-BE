from django.db import models

from common.models import CommonModel
from questions.models import Question


class Notification(CommonModel):
    message = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
