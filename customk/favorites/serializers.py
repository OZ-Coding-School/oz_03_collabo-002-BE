from rest_framework import serializers
from .models import Favorite
from classes.serializers import ClassSerializer


class FavoriteSerializer(serializers.ModelSerializer):  # type: ignore
    klass = ClassSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'klass']
