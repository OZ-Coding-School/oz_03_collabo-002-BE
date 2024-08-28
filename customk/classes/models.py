from typing import Any, Dict, Optional

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Avg

from common.models import CommonModel


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=10, default="USD")
    rate = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self) -> str:
        return f"{self.currency}: {self.rate}"


class Class(CommonModel):
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True)
    max_person = models.IntegerField(blank=False, default=0)
    require_person = models.IntegerField(blank=False, default=0)
    price = models.IntegerField(blank=False, default=0)
    address = models.JSONField(encoder=DjangoJSONEncoder, default=dict, blank=True)
    class_type = models.JSONField(encoder=DjangoJSONEncoder, default=list, blank=True)

    is_viewed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    def get_price_in_usd(self) -> Optional[float]:
        exchange_rate: Optional[ExchangeRate] = ExchangeRate.objects.filter(
            currency="USD"
        ).first()
        if exchange_rate:
            return round(float(self.price) / float(exchange_rate.rate), 2)
        return None

    @property
    def average_rating(self) -> Optional[float]:
        avg: Optional[float] = (
            self.reviews.aggregate(average=Avg("rating"))["average"] or 0
        )

        if avg is None:
            return None
        return round(float(avg), 1)

    @property
    def formatted_address(self) -> str:
        address = self.address or {}
        state = address.get("state", "")
        city = address.get("city", "")
        street = address.get("street", "")
        return f"{state} {city} {street}".strip()


class ClassDate(models.Model):
    class_id = models.ForeignKey(Class, related_name="dates", on_delete=models.CASCADE)
    start_date = models.DateField(blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)
    person = models.IntegerField(blank=False, default=0)


class ClassImages(models.Model):
    class_id = models.ForeignKey(Class, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=2000)

    def __str__(self) -> str:
        return f"{self.class_id.title}"
