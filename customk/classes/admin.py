from django.contrib import admin, messages
from .models import Class, ClassDate, ClassImages, ExchangeRate


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
        "price_in_usd",
        "address",
        "is_viewed_badge",
        "average_rating",
    )

    def price_in_usd(self, obj):
        usd_price = obj.get_price_in_usd()
        return usd_price

    price_in_usd.short_description = "가격 (USD)"

    def is_viewed_badge(self, obj):
        if obj.is_viewed:
            return "✅"
        else:
            return "❗"

    is_viewed_badge.short_description = "조회 상태"

    def changelist_view(self, request, extra_context=None):
        unviewed_classes_count = Class.objects.filter(is_viewed=False).count()

        if unviewed_classes_count > 0:
            messages.warning(
                request, f"{unviewed_classes_count}개의 조회되지 않은 클래스가 있습니다."
            )

        return super().changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        course = self.get_object(request, object_id)
        if course and not course.is_viewed:
            course.is_viewed = True
            course.save()

        return super().change_view(request, object_id, form_url, extra_context)

    inlines = [ClassDateInline, ClassImagesInline]


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("currency", "rate")
