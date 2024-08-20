from django.contrib import admin
from .models import Reaction


@admin.register(Reaction)
class ReactionModel(admin.ModelAdmin):
    list_display = ("id", "review", "reaction", "get_review_reactions")

    def get_review_reactions(self, obj):
        reactions = Reaction.get_review_reactions(obj.review)
        return f"Likes: {reactions['likes_count']}, Dislikes: {reactions['dislikes_count']}"

    get_review_reactions.short_description = "Review Reactions"
