import base64
import uuid
from datetime import timedelta

from rest_framework import serializers

from classes.models import Class
from common.services.ncp_api_conf import ObjectStorage
from config.logger import logger
from users.serializers.user_serializer import UserSerializer

from .models import Review, ReviewImage


def upload_image_to_object_storage(base64_image: str) -> str:
    obj_client = ObjectStorage()

    try:
        formatted, img_str = base64_image.split(";base64,")
        ext = formatted.split("/")[-1]
        decoded_image = base64.b64decode(img_str)
    except (ValueError, IndexError) as e:
        logger.error(f"Invalid base64 image format: {str(e)}")
        raise serializers.ValidationError(
            {"reply_image_base64": "Invalid base64 image format"}
        )

    file_name = f"{uuid.uuid4()}.{ext}"

    bucket_name = "customk-imagebucket"
    object_name = f"reply-images/{file_name}"
    try:
        status_code, image_url = obj_client.put_object(
            bucket_name, object_name, decoded_image
        )
        if status_code != 200:
            error_message = f"Failed to upload image. Status code: {status_code}"
            logger.error(error_message)
            raise serializers.ValidationError({"reply_image": error_message})
        return image_url
    except Exception as e:
        logger.error(f"Unexpected error during ObjectStorage upload: {str(e)}")
        raise serializers.ValidationError(
            {"reply_image": "An unexpected error occurred"}
        )


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ["id", "image_url"]

    def get_image_url(self, obj):
        return obj.image_url

    def validate(self, data):
        review = data.get("review")
        if ReviewImage.objects.filter(review=review).count() >= 4:
            raise serializers.ValidationError(
                "A review can only have a maximum of 4 images."
            )
        return data


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, required=False)
    user = UserSerializer(read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "review", "rating", "user", "images"]

    def create(self, validated_data):
        images_data64 = validated_data.pop("images", [])
        class_id = validated_data.pop("class_id")

        try:
            class_instance = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            raise serializers.ValidationError({"class_id": "Invalid class ID."})

        review = Review.objects.create(class_id=class_instance, **validated_data)

        for image_data64 in images_data64:
            image_url = upload_image_to_object_storage(image_data64["image_url"])
            ReviewImage.objects.create(review=review, image_url=image_url)

        return review
