from typing import Any, Dict, Optional

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse

from .forms import ClassImagesForm
from .models import Category, Class, ClassDate, ClassImages, ExchangeRate, Genre
from .utils import upload_image_to_object_storage


class ClassDateInline(admin.TabularInline):  # type: ignore
    model = ClassDate
    extra = 0


class ClassImagesInline(admin.TabularInline):  # type: ignore
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

    def price_in_usd(self, obj: Class) -> Optional[float]:
        usd_price = obj.get_price_in_usd()
        return usd_price

    price_in_usd.short_description = "가격 (USD)"  # type: ignore

    def is_viewed_badge(self, obj: Class) -> str:
        if obj.is_viewed:
            return "✅"
        else:
            return "❗"

    is_viewed_badge.short_description = "조회 상태"  # type: ignore

    def changelist_view(
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
    ) -> HttpResponse:
        unviewed_classes_count = Class.objects.filter(is_viewed=False).count()

        if unviewed_classes_count > 0:
            messages.warning(
                request,
                f"{unviewed_classes_count}개의 조회되지 않은 클래스가 있습니다.",
            )

        return super().changelist_view(request, extra_context=extra_context)

    def change_view(
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> HttpResponse:
        course = self.get_object(request, object_id)
        if course and not course.is_viewed:
            course.is_viewed = True
            course.save()

        return super().change_view(request, object_id, form_url, extra_context)

    inlines = [ClassDateInline, ClassImagesInline]


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("currency", "rate")


@admin.register(ClassImages)
class ClassImagesAdmin(admin.ModelAdmin):
    form = ClassImagesForm
    list_display = [
        "class_id",
        "thumbnail_image_url",
        "description_image_url",
        "detail_image_url",
    ]
    search_fields = ["class_id"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if form.cleaned_data.get("thumbnail_image"):
            thumbnail_image = form.cleaned_data["thumbnail_image"]
            thumbnail_url = upload_image_to_object_storage(thumbnail_image)
            obj.thumbnail_image_url = thumbnail_url

        if form.cleaned_data.get("description_image"):
            description_image = form.cleaned_data["description_image"]
            description_url = upload_image_to_object_storage(description_image)
            obj.description_image_url = description_url

        if form.cleaned_data.get("detail_image"):
            detail_image = form.cleaned_data["detail_image"]
            detail_url = upload_image_to_object_storage(detail_image)
            obj.detail_image_url = detail_url

        obj.save()


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
