from rest_framework import serializers
from .models import Review, ReviewImage
from users.models import User


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ["id", "image_url"]


class ReviewSerializer(serializers.ModelSerializer):
    # TODO user_id로 받고 있지만 user_name으로 받을 생각을 해야할 수 있음
    images = ReviewImageSerializer(many=True, required=False)
    user = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = Review
        fields = "__all__"

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        review = Review.objects.create(**validated_data)

        for image_data in images_data:
            ReviewImage.objects.create(review=review, **image_data)

        return review
