from django.contrib import admin
from typing import Dict
from .models import Reaction


@admin.register(Reaction)
class ReactionModel(admin.ModelAdmin): # type: ignore
    list_display = ("id", "review", "reaction", "get_review_reactions")

    def get_review_reactions(self, obj: Reaction) -> str:
        reactions: Dict[str, int] = Reaction.get_review_reactions(obj.review)
        return f"Likes: {reactions['likes_count']}, Dislikes: {reactions['dislikes_count']}"

    get_review_reactions.short_description = "Review Reactions" # type: ignore
