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

    class Meta:
        model = Class
        fields = "__all__"

    def get_is_new(self, obj):
        return timezone.now() - obj.created_at <= timedelta(days=30)

    def get_price_in_usd(self, obj):
        usd_price = obj.get_price_in_usd()
        return usd_price

    def create(self, validated_data):
        dates_data = validated_data.pop("dates", [])
        images_data = validated_data.pop("images", [])

        class_instance = Class.objects.create(**validated_data)

        for date_data in dates_data:
            ClassDate.objects.create(course=class_instance, **date_data)

        for image_data in images_data:
            ClassImages.objects.create(course=class_instance, **image_data)

        return class_instance
