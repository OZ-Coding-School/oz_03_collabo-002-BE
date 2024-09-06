from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(help_text="에러 메시지")
    details = serializers.JSONField(help_text="상세 에러 정보", required=False)
