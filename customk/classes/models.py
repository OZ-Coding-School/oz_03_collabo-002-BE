from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from common.models import CommonModel
from django.db.models import Avg


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=10, default="USD")
    rate = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return f"{self.currency}: {self.rate}"


class Class(CommonModel):
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True)
    max_person = models.IntegerField(blank=False, default=0)
    require_person = models.IntegerField(blank=False, default=0)
    price = models.IntegerField(blank=False, default=0)
    address = models.JSONField(encoder=DjangoJSONEncoder, default=dict, blank=True)

    is_viewed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_price_in_usd(self):
        exchange_rate = ExchangeRate.objects.filter(currency="USD").first()
        if exchange_rate:
            return round(self.price / exchange_rate.rate, 2)
        return None

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(average=Avg("rating"))["average"] or 0
        return round(avg, 1)


class ClassDate(models.Model):
    # TODO person field 수정에 대해 논의
    class_id = models.ForeignKey(Class, related_name="dates", on_delete=models.CASCADE)
    start_date = models.DateField(blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)
    person = models.IntegerField(blank=False, default=0)


class ClassImages(models.Model):
    class_id = models.ForeignKey(Class, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=2000)

    def __str__(self):
        return f"{self.class_id.title}"
