from django.contrib import admin
from .models import Review, ReviewImage


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    max_num = 5
    readonly_fields = ("image_url",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "class_id", "rating", "created_at")
    list_filter = ("rating", "created_at", "class_id")
    search_fields = ("user__name", "class_id__title", "review")
    inlines = [ReviewImageInline]
    readonly_fields = ("rating",)
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'class_id', 'rating')
        }),
        ('리뷰 내용', {
            'fields': ('review',),
            'description': '리뷰 내용을 여기에 입력하세요.'
        }),
    )


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ("review", "image_url")
    search_fields = ("review__review",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
