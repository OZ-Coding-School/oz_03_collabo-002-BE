from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    name = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("name", "email", "password")

    def validate(self, data):
        user = User(**data)

        errors = dict()
        try:
            validate_password(password=data["password"], user=user)
        except ValidationError as e:
            errors["password"] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(data)

    def create(self, validated_data):
        user = User(**validated_data)

        user.set_password(validated_data["password"])
        user.save()
        return user


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name", "email")


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name",)
