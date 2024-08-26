from typing import Optional, Dict, Any
from django.http import HttpRequest, HttpResponse
from django.contrib import admin, messages

from .models import Class, ClassDate, ClassImages, ExchangeRate


class ClassDateInline(admin.TabularInline): # type: ignore
    model = ClassDate
    extra = 0


class ClassImagesInline(admin.TabularInline): # type: ignore
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
        "formatted_address",
        "is_viewed_badge",
        "average_rating",
    )

    def price_in_usd(self, obj: Class) -> Optional[float]:
        usd_price = obj.get_price_in_usd()
        return usd_price

    price_in_usd.short_description = "가격 (USD)" # type: ignore

    def is_viewed_badge(self, obj: Class) -> str:
        if obj.is_viewed:
            return "✅"
        else:
            return "❗"

    is_viewed_badge.short_description = "조회 상태" # type: ignore

    def changelist_view(self, request: HttpRequest, extra_context: Optional[Dict[str, Any]]=None) -> HttpResponse:
        unviewed_classes_count = Class.objects.filter(is_viewed=False).count()

        if unviewed_classes_count > 0:
            messages.warning(
                request,
                f"{unviewed_classes_count}개의 조회되지 않은 클래스가 있습니다.",
            )

        return super().changelist_view(request, extra_context=extra_context)

    def change_view(self, request: HttpRequest, object_id: str, form_url: str="", extra_context: Optional[Dict[str, Any]] = None) -> HttpResponse:
        course = self.get_object(request, object_id)
        if course and not course.is_viewed:
            course.is_viewed = True
            course.save()

        return super().change_view(request, object_id, form_url, extra_context)

    inlines = [ClassDateInline, ClassImagesInline]


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin): # type: ignore
    list_display = ("currency", "rate")
