from django.contrib import admin

from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("user_id", "class_id", "question_title", "created_at", "updated_at")
    list_filter = ("class_id", "created_at", "user_id")
    search_fields = ("user_id__name", "class_id__title", "question", "question_title")
    fieldsets = (
        ("기본 정보", {"fields": ("user_id", "class_id")}),
        ("질문 내용", {"fields": ("question_title", "question")}),
        ("답변 내용", {"fields": ("answer_title", "answer"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user_id = request.user
        super().save_model(request, obj, form, change)
