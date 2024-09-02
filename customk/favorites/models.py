from django.db import models

from classes.models import Class
from common.models import CommonModel
from users.models import User


class Favorite(CommonModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    class_id = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "class_id"], name="unique_users_class"
            )
        ]

    def __str__(self):
        klass = Class.objects.filter(pk=self.class_id).first()
        return f"{self.user.username} likes {klass.title}"
