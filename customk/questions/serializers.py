from rest_framework import serializers

from users.models import User

from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)  # created_at 필드 read_only
    class_id = serializers.IntegerField(read_only=True)  # class_id 필드 read_only
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = "__all__"
