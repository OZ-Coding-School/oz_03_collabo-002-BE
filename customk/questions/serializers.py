from rest_framework import serializers
from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Question
        fields = "__all__"
