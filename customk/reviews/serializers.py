from rest_framework import serializers
from .models import Review, ReviewImage


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ["id", "image_url"]


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, required=False)

    class Meta:
        model = Review
        fields = ["id", "review", "rating", "images"]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        review = Review.objects.create(**validated_data)

        for image_data in images_data:
            ReviewImage.objects.create(review=review, **image_data)

        return review
