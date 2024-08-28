import base64
import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from common.services.ncp_api_conf import ObjectStorage
from config.logger import logger
from users.models import User


def upload_image_to_object_storage(base64_image: str) -> str:
    obj_client = ObjectStorage()

    try:
        formatted, img_str = base64_image.split(";base64,")
        ext = formatted.split("/")[-1]
        decoded_image = base64.b64decode(img_str)
    except (ValueError, IndexError):
        raise serializers.ValidationError(
            {"profile_image_base64": "Invalid base64 image format"}
        )

    file_name = f"{uuid.uuid4()}.{ext}"

    bucket_name = "customk-imagebucket"
    object_name = f"profile-images/{file_name}"
    try:
        status_code, image_url = obj_client.put_object(
            bucket_name, object_name, decoded_image
        )
        if status_code != 200:
            error_message = f"Failed to upload image. Status code: {status_code}"
            logger.error(error_message)
            raise serializers.ValidationError({"profile_image": error_message})
        return image_url
    except Exception as e:
        logger.error(f"Unexpected error during ObjectStorage upload: {str(e)}")
        raise serializers.ValidationError(
            {"profile_image": "An unexpected error occurred"}
        )


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    name = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)
    profile_image = serializers.CharField(write_only=True, required=False)
    profile_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "password",
            "profile_image",
            "profile_image_url",
        )

    def get_profile_image_url(self, obj):
        return obj.profile_image

    def velidate(self, data):
        user = User(**data)

        errors = dict()
        try:
            validate_password(password=data["password"], user=user)
        except ValidationError as e:
            errors["password"] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(data)

    @transaction.atomic
    def create(self, validated_data):
        profile_image_base64 = validated_data.pop("profile_image", None)

        user = User(**validated_data)
        user.set_password(validated_data["password"])

        if profile_image_base64:
            user.profile_image = upload_image_to_object_storage(profile_image_base64)

        user.save()
        return user


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email", "profile_image")


class UserUpdateSerializer(serializers.ModelSerializer):
    profile_image = serializers.CharField(write_only=True, required=False)
    profile_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ("name", "profile_image", "profile_image_url")

    def get_profile_image_url(self, obj):
        return obj.profile_image

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        base64_image = validated_data.pop("profile_image", None)

        if instance.profile_image:
            obj = ObjectStorage()
            obj_status_code = obj.delete_object(instance.profile_image)

            if obj_status_code != 204:
                raise ValidationError(
                    {
                        "profile_image": "Failed to delete existing profile image. Status code: {obj_status_code}"
                    }
                )

        if base64_image:
            instance.profile_image = upload_image_to_object_storage(base64_image)

        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise AuthenticationFailed("Invalid login credentials")
            if not user.is_active:
                raise AuthenticationFailed("User account is deactivated")

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            return {"user": user}
        else:
            raise serializers.ValidationError('Must include "email" and "password"')
