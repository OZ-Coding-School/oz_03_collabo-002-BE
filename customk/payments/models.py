from django.db import models

from common.models import CommonModel
from django.core.exceptions import ValidationError


class ReferralCode(CommonModel):
    code = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
    )

    def clean(self):
        if self.discount_rate > 100:
            raise ValidationError('Discount rate must be between 0 and 100 percent.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Payment(CommonModel):
    # 주문 정보
    order_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)

    # 결제 수단 및 관련 정보
    payment_method = models.CharField(max_length=50)  # paypal or another method
    payer_email = models.EmailField(max_length=255, blank=True, null=True)

    # 클래스 관련 정보
    user_id = models.IntegerField()
    class_id = models.IntegerField()
    options = models.JSONField(blank=True, null=True)
    class_date_id = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)

    # 추가 정보
    referral_code = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.payment_method} payment for order {self.order_id}"
