from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from classes.models import Class
from common.models import CommonModel
from users.models import User


class Review(CommonModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_id = models.ForeignKey(
        Class, related_name="reviews", on_delete=models.CASCADE
    )
    review = models.TextField()
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0.5")),  # 최소 0.5점
            MaxValueValidator(Decimal("5.0")),  # 최대 5점
        ],
    )

    def __str__(self) -> str:
        return f"Review: {self.review}, Rating: {self.rating}"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, related_name="images", on_delete=models.CASCADE)
    image_url = models.CharField()

    def __str__(self) -> str:
        return f"Image for Review {self.review.id}: {self.image_url}"

    def save(self, *args, **kwargs):
        try:
            if ReviewImage.objects.filter(review=self.review).count() >= 4:
                raise ValidationError("A review can only have a maximum of 4 images.")
            super().save(*args, **kwargs)
        except ValidationError as e:
            print(f"ValidationError: {e}")
            raise
