from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from classes.models import Class
from common.models import CommonModel


class Review(CommonModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.DecimalField(
        max_digits=2,  # 최대 자리수 (5.0, 4.5 등 최대 2자리)
        decimal_places=1,  # 소수점 아래 한 자리수만 허용
        validators=[
            MinValueValidator(Decimal("0.5")),  # 최소 0.5점
            MaxValueValidator(Decimal("5.0")),  # 최대 5점
        ],
    )

    def __str__(self):
        return f"Review: {self.review}, Rating: {self.rating}"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Image for Review {self.review.id}: {self.image_url}"
