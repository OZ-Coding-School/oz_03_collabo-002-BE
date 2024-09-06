from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification

from .models import Question


@receiver(post_save, sender=Question)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            message=f"새로운 질문이 생성되었습니다: {instance.question_title}",
            question=instance,
        )
