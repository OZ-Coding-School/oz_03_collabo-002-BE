from rest_framework import serializers

from classes.models import Class
from users.models import User

from .models import Review, ReviewImage


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ["id", "image_url"]


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, required=False)
    user = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = Review
        fields = "__all__"

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        class_id = validated_data.pop("class_id")

        try:
            class_instance = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            raise serializers.ValidationError({"class_id": "Invalid class ID."})

        review = Review.objects.create(class_id=class_instance, **validated_data)

        for image_data in images_data:
            ReviewImage.objects.create(review=review, **image_data)

        return review
