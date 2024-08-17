from django.contrib import admin, messages
from .models import Class, ClassDate, ClassImages


class ClassDateInline(admin.TabularInline):
    model = ClassDate
    extra = 0


class ClassImagesInline(admin.TabularInline):
    model = ClassImages
    extra = 0


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):  # type: ignore
    list_display = (
        "title",
        "description",
        "max_person",
        "require_person",
        "price",
        "address",
        "is_viewed_badge",
    )

    def is_viewed_badge(self, obj):
        if obj.is_viewed:
            return "✅"
        else:
            return "❗"

    is_viewed_badge.short_description = "조회 상태"

    def changelist_view(self, request, extra_context=None):
        # 조회되지 않은 클래스의 수를 계산
        unviewed_classes_count = Class.objects.filter(is_viewed=False).count()

        # 조회되지 않은 클래스가 있을 경우 관리자에게 경고 메시지를 표시
        if unviewed_classes_count > 0:
            messages.warning(
                request, f"{unviewed_classes_count}개의 조회되지 않은 클래스가 있습니다."
            )

        return super().changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # 관리자가 클래스를 조회할 때 is_viewed 필드를 True로 업데이트
        course = self.get_object(request, object_id)
        if course and not course.is_viewed:
            course.is_viewed = True
            course.save()

        return super().change_view(request, object_id, form_url, extra_context)

    inlines = [ClassDateInline, ClassImagesInline]
