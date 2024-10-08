import math
from decimal import Decimal
from typing import Optional

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Avg, JSONField

from common.models import CommonModel


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=10, default="USD")
    rate = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self) -> str:
        return f"{self.currency}: {self.rate}"


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Class(CommonModel):
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True)
    max_person = models.PositiveIntegerField(blank=False, default=0)
    require_person = models.PositiveIntegerField(blank=False, default=0)
    price = models.IntegerField(blank=False, default=0)
    address = models.CharField(
        max_length=255, help_text="주소를 '도, 시, 구' 형식으로 입력해주세요."
    )
    class_type = models.JSONField(encoder=DjangoJSONEncoder, default=list, blank=True)
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE, null=True, blank=True)
    category = models.ManyToManyField("Category", blank=True)  # type: ignore
    discount_rate = models.PositiveIntegerField(default=0)
    is_viewed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    def get_price_in_usd(self) -> Optional[float]:
        exchange_rate: Optional[ExchangeRate] = ExchangeRate.objects.filter(
            currency="USD"
        ).first()
        if not exchange_rate:
            return None

        price_in_usd = Decimal(self.price) / Decimal(exchange_rate.rate)
        rounded_price = math.ceil(price_in_usd)
        return rounded_price


class ClassDate(models.Model):
    class_id = models.ForeignKey(Class, related_name="dates", on_delete=models.CASCADE)
    start_date = models.DateField(blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)
    person = models.PositiveIntegerField(blank=False, default=0)


class ClassImages(models.Model):
    class_id = models.ForeignKey(Class, related_name="images", on_delete=models.CASCADE)
    description_image_urls = JSONField(blank=True, default=list)
    detail_image_urls = JSONField(blank=True, default=list)
    thumbnail_image_urls = JSONField(blank=True, default=list)

    def __str__(self) -> str:
        return f"{self.class_id.title}"
