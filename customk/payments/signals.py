from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import PaymentNotification

from .models import Payment


@receiver(post_save, sender=Payment)
def create_payment_notification(sender, instance, created, **kwargs):
    if created:
        PaymentNotification.objects.create(
            message=f"새로운 결제가 생성되었습니다: 주문 ID {instance.order_id}, 금액 {instance.amount} {instance.currency}",
            payment=instance,
        )
