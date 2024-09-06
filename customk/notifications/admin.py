from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("message", "class_field", "created_at", "is_read")
    list_filter = ("is_read", "question__class_id")
    search_fields = ("message", "question__class_id__title")

    def class_field(self, obj):
        return obj.question.class_id.title  # Access class_id title through the question

    class_field.admin_order_field = "question__class_id__title" # type: ignore
    class_field.short_description = "Class Title" # type: ignore
