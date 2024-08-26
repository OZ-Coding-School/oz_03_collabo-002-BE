from typing import Optional, Any
from django.contrib import admin

from reactions.models import Reaction

from .models import Review, ReviewImage


class ReviewImageInline(admin.TabularInline):  # type: ignore
    model = ReviewImage
    extra = 1
    max_num = 5
    readonly_fields = ("image_url",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("user", "class_id", "rating", "created_at", "likes_count")
    list_filter = ("rating", "created_at", "class_id")
    search_fields = ("user__name", "class_id__title", "review")
    inlines = [ReviewImageInline]
    fieldsets = (
        ("기본 정보", {"fields": ("user", "class_id", "rating")}),
        (
            "리뷰 내용",
            {"fields": ("review",), "description": "리뷰 내용을 여기에 입력하세요."},
        ),
    )

    def likes_count(self, obj: Review) -> int:
        reactions = Reaction.get_review_reactions(obj)
        return reactions["likes_count"]

    likes_count.short_description = "좋아요 수" # type: ignore


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("review", "image_url")
    search_fields = ("review__review",)
