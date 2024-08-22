from django.db.models import Avg
from rest_framework import serializers
from .models import Class, ClassDate, ClassImages
from django.utils import timezone
from datetime import timedelta


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


class ClassSerializer(serializers.ModelSerializer):
    dates = ClassDateSerializer(many=True, required=False)
    images = ClassImagesSerializer(many=True, required=False)
    is_new = serializers.SerializerMethodField()
    price_in_usd = serializers.SerializerMethodField()
    is_best = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = "__all__"

    def get_is_new(self, obj):
        return timezone.now() - obj.created_at <= timedelta(days=30)

    def get_price_in_usd(self, obj):
        usd_price = obj.get_price_in_usd()
        return usd_price

    def get_average_rating(self, obj):
        one_month_ago = timezone.now() - timedelta(days=30)
        recent_reviews = obj.reviews.filter(created_at__gte=one_month_ago)

        average_rating = recent_reviews.aggregate(average=Avg('rating'))['average'] or 0

        return round(average_rating, 1)

    def get_is_best(self, obj):
        one_month_ago = timezone.now() - timedelta(days=30)
        recent_reviews = obj.reviews.filter(created_at__gte=one_month_ago)

        average_rating = recent_reviews.aggregate(average=Avg('rating'))['average'] or 0

        return average_rating >= 3.5

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['average_rating'] = self.get_average_rating(instance)
        representation['is_best'] = self.get_is_best(instance)

        return representation

    def create(self, validated_data):
        dates_data = validated_data.pop("dates", [])
        images_data = validated_data.pop("images", [])

        class_instance = Class.objects.create(**validated_data)

        for date_data in dates_data:
            ClassDate.objects.create(class_id=class_instance, **date_data)

        for image_data in images_data:
            ClassImages.objects.create(class_id=class_instance, **image_data)

        return class_instance
