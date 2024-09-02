from rest_framework import serializers

from classes.models import Class
from classes.serializers import ClassSerializer

from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    klass = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ["id", "user", "class_id", "klass"]

    def get_klass(self, obj):
        try:
            class_instance = Class.objects.get(id=obj.class_id)
            return ClassSerializer(class_instance).data
        except Class.DoesNotExist:
            return None
