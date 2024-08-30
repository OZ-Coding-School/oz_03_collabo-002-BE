from typing import Any, Dict, Optional

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.utils.html import format_html

from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "class_id",
        "question_title",
        "created_at",
        "updated_at",
        "answer_icon",
    )
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

    def answer_icon(self, obj):
        if obj.answer:
            return format_html('<span style="font-size: 1.2em; color: #00FF00;">✅</span>')
        else:
            return format_html('<span style="font-size: 1.2em; color: red;">❌</span>')

    answer_icon.short_description = "답변 상태"  # type: ignore

    def changelist_view(
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
    ) -> HttpResponse:
        unanswered_questions_count = Question.objects.filter(
            answer=''
        ).count()

        if unanswered_questions_count > 0:
            messages.warning(
                request,
                f"{unanswered_questions_count}개의 답변되지 않은 질문이 있습니다.",
            )

        return super().changelist_view(request, extra_context=extra_context)

    def change_view(
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> HttpResponse:
        question = self.get_object(request, object_id)
        if question and question.answer is None:
            messages.info(request, "이 질문에는 아직 답변이 없습니다.")

        return super().change_view(request, object_id, form_url, extra_context)
