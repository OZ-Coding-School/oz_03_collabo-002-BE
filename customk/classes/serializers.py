import base64
import uuid
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework import serializers

from common.services.ncp_api_conf import ObjectStorage
from config.logger import logger
from payments.models import Payment

from .models import Category, Class, ClassDate, ClassImages


def upload_image_to_object_storage(base64_image: str) -> str:
    obj_client = ObjectStorage()

    try:
        formatted, img_str = base64_image.split(";base64,")
        ext = formatted.split("/")[-1]
        decoded_image = base64.b64decode(img_str)
    except (ValueError, IndexError) as e:
        logger.error(f"Invalid base64 image format: {str(e)}")
        raise serializers.ValidationError(
            {"class_image_base64": "Invalid base64 image format"}
        )

    file_name = f"{uuid.uuid4()}.{ext}"

    bucket_name = "customk-imagebucket"
    object_name = f"class-images/{file_name}"
    try:
        status_code, image_url = obj_client.put_object(
            bucket_name, object_name, decoded_image
        )
        if status_code != 200:
            error_message = f"Failed to upload image. Status code: {status_code}"
            logger.error(error_message)
            raise serializers.ValidationError({"class_image": error_message})
        return image_url
    except Exception as e:
        logger.error(f"Unexpected error during ObjectStorage upload: {str(e)}")
        raise serializers.ValidationError(
            {"class_image": "An unexpected error occurred"}
        )


class ClassDateSerializer(serializers.ModelSerializer):
    class_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ClassDate
        fields = "__all__"


class ClassImagesSerializer(serializers.ModelSerializer):
    class_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ClassImages
        fields = "__all__"

    def get_image_urls(self, obj):
        return {
            "thumbnail_image_url": obj.thumbnail_image_url,
            "description_image_url": obj.description_image_url,
            "additional_image_url": obj.additional_image_url,
        }


class ClassSerializer(serializers.ModelSerializer):
    dates = ClassDateSerializer(many=True, required=False)
    images = ClassImagesSerializer(many=True, required=False)
    is_new = serializers.SerializerMethodField()
    price_in_usd = serializers.SerializerMethodField()
    is_best = serializers.SerializerMethodField()
    genre = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Category.objects.all()
    )
    average_rating = serializers.FloatField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    is_popular = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = "__all__"

    def get_genre(self, obj):
        return obj.genre.name if obj.genre else None

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_is_new(self, obj):
        return timezone.now() - obj.created_at <= timedelta(days=30)

    def get_price_in_usd(self, obj):
        usd_price = obj.get_price_in_usd()
        return usd_price

    def get_average_rating(self, obj):
        one_month_ago = timezone.now() - timedelta(days=30)
        recent_reviews = obj.reviews.filter(created_at__gte=one_month_ago)

        average_rating = recent_reviews.aggregate(average=Avg("rating"))["average"] or 0

        return round(average_rating, 1)

    def get_is_best(self, obj):
        one_month_ago = timezone.now() - timedelta(days=30)
        recent_reviews = obj.reviews.filter(created_at__gte=one_month_ago)

        average_rating = recent_reviews.aggregate(average=Avg("rating"))["average"] or 0

        return average_rating >= 3.5

    def get_is_popular(self, obj):
        popular_classes = cache.get("popular_classes", None)

        if popular_classes is None:
            one_month_ago = timezone.now() - timedelta(days=30)

            classes_with_payments = (
                Payment.objects.filter(created_at__gte=one_month_ago)
                .values("class_id")
                .annotate(payment_count=Count("id"))
                .order_by("-payment_count")
            )

            total_classes = len(classes_with_payments)
            top_20_percent_count = max(1, int(total_classes * 0.2))

            popular_class_ids = [
                entry["class_id"]
                for entry in classes_with_payments[:top_20_percent_count]
            ]

            cache.set("popular_classes", popular_class_ids, timeout=60 * 60 * 24 * 14)
            popular_classes = popular_class_ids

        is_popular = obj.id in popular_classes
        print(f"Class ID: {obj.id}, Is Popular: {is_popular}")
        return is_popular

    def create(self, validated_data):
        dates_data = validated_data.pop("dates", [])
        images_data64 = validated_data.pop("images", [])
        categories_data = validated_data.pop("category", [])

        class_instance = Class.objects.create(**validated_data)

        class_instance.category.set(categories_data)

        for date_data in dates_data:
            ClassDate.objects.create(class_id=class_instance, **date_data)

        for image_data64 in images_data64:
            thumbnail_url = upload_image_to_object_storage(
                image_data64["thumbnail_image_url"]
            )
            description_url = upload_image_to_object_storage(
                image_data64["description_image_url"]
            )
            detail_image_url = upload_image_to_object_storage(
                image_data64["detail_image_url"]
            )

            ClassImages.objects.create(
                class_id=class_instance,
                thumbnail_image_url=thumbnail_url,
                description_image_url=description_url,
                detail_image_url=detail_image_url,
            )

        return class_instance
