from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.models import CommonModel
from .utils import get_exchange_rate, convert_to_usd

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Class(CommonModel):
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True)
    max_person = models.IntegerField(blank=False, default=0)
    require_person = models.IntegerField(blank=False, default=0)
    price = models.IntegerField(blank=False, default=0)
    # address = models.TextField(blank=False, default="")
    address = models.JSONField(
        encoder=DjangoJSONEncoder,
        default=dict,
        blank=True
    )

    is_viewed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


    @property
    def price_in_usd(self):
        api_key = "530f86837ccd5ef16f5e7de0"  # 여러분의 API 키를 여기에 입력하세요
        exchange_rates = get_exchange_rate(api_key)
        usd_rate = exchange_rates.get('USD', 1)
        return convert_to_usd(self.price, usd_rate)


class ClassDate(models.Model):
    # TODO person field 수정에 대해 논의
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


