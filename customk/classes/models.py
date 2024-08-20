from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Class(models.Model):
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True)
    max_person = models.IntegerField(blank=False, default=0)
    require_person = models.IntegerField(blank=False, default=0)
    price = models.IntegerField(blank=False, default=0)
    address = models.TextField(blank=False, default="")

    is_viewed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ClassDate(models.Model):
    course = models.ForeignKey(Class, related_name="dates", on_delete=models.CASCADE)
    start_date = models.DateField(blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)
    person = models.IntegerField(blank=False, default=0)


class ClassImages(models.Model):
    course = models.ForeignKey(Class, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=2000)

    def __str__(self):
        return f"{self.course.title}"


# 시그널 핸들러 추가
@receiver(post_save, sender=Class)
def send_notification(sender, instance, created, **kwargs):
    if created:
        # Channel Layer를 가져옵니다.
        channel_layer = get_channel_layer()

        # 알림 메시지 생성
        message = {
            "type": "send_notification",
            "notification": f"새로운 클래스가 등록되었습니다: {instance.title}",
        }

        # 'notifications' 그룹에 메시지 전송
        async_to_sync(channel_layer.group_send)("notifications", message)
