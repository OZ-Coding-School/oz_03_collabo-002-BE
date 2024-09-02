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
        "thumbnail_image_urls",
        "description_image_urls",
        "detail_image_urls",
    ]
    search_fields = ["class_id"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Handle thumbnail image
        if form.cleaned_data.get("thumbnail_image"):
            thumbnail_image = form.cleaned_data["thumbnail_image"]
            thumbnail_url = upload_image_to_object_storage(thumbnail_image)
            thumbnail_image_urls = obj.thumbnail_image_urls or []
            thumbnail_image_urls.append(thumbnail_url)
            obj.thumbnail_image_urls = thumbnail_image_urls

        # Handle description image
        if form.cleaned_data.get("description_image"):
            description_image = form.cleaned_data["description_image"]
            description_url = upload_image_to_object_storage(description_image)
            description_image_urls = obj.description_image_urls or []
            description_image_urls.append(description_url)
            obj.description_image_urls = description_image_urls

        # Handle detail image
        if form.cleaned_data.get("detail_image"):
            detail_image = form.cleaned_data["detail_image"]
            detail_url = upload_image_to_object_storage(detail_image)
            detail_image_urls = obj.detail_image_urls or []
            detail_image_urls.append(detail_url)
            obj.detail_image_urls = detail_image_urls

        obj.save()


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
