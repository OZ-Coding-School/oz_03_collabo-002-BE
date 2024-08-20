from rest_framework import serializers
from .models import Class, ClassDate, ClassImages
from django.utils import timezone
from datetime import timedelta


class ClassDateSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ClassDate
        fields = "__all__"


class ClassImagesSerializer(serializers.ModelSerializer):
    # 읽기 전용으로 인식되지 않고 입력으로만 사용
    # course 필드는 읽기 전용으로 처리되고, create 메서드에서 직접 할당
    course = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ClassImages
        fields = "__all__"


class ClassSerializer(serializers.ModelSerializer):
    dates = ClassDateSerializer(many=True, required=False)
    images = ClassImagesSerializer(many=True, required=False)
    is_new = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = "__all__"

    def get_is_new(self, obj):
        # 클래스가 생성된 지 30일 이내라면 True 반환
        return timezone.now() - obj.created_at <= timedelta(days=30)

    def create(self, validated_data):
        dates_data = validated_data.pop("dates", [])
        images_data = validated_data.pop("images", [])

        class_instance = Class.objects.create(**validated_data)

        for date_data in dates_data:
            ClassDate.objects.create(course=class_instance, **date_data)

        for image_data in images_data:
            ClassImages.objects.create(course=class_instance, **image_data)

        return class_instance
