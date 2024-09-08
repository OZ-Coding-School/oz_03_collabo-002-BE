from django.db import models

from common.models import CommonModel
from payments.models import Payment
from questions.models import Question


class QuestionNotification(CommonModel):
    message = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message


class PaymentNotification(CommonModel):
    message = models.CharField(max_length=255)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        null=True,
    )
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
