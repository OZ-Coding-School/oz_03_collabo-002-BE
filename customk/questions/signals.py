from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Question


@receiver(post_save, sender=Question)
# TODO 관리자 페이지 알림
def question_post_save(sender, instance, created, **kwargs):
    if created:
        cache.set("new_question_created", True, 300)  # 5분 동안 캐시에 저장
