from typing import Dict

from django.db import models
from django.db.models import Count, Q

from common.models import CommonModel
from reviews.models import Review


class Reaction(CommonModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    review = models.ForeignKey("reviews.Review", on_delete=models.CASCADE)

    LIKE = 1
    DISLIKE = -1
    NO_REACTION = 0

    REACTON_CHOICES = (
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
        (NO_REACTION, "No Reaction"),
    )

    reaction = models.IntegerField(choices=REACTON_CHOICES, default=NO_REACTION)

    @staticmethod
    def get_review_reactions(review: Review) -> Dict[str, int]:
        reactions = Reaction.objects.filter(review=review).aggregate(
            likes_count=Count("pk", filter=Q(reaction=Reaction.LIKE)),
            dislikes_count=Count("pk", filter=Q(reaction=Reaction.DISLIKE)),
        )
        return reactions
