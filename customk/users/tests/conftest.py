import pytest
from rest_framework.test import APIClient

from users.serializers.user_serializer import UserSerializer


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_user(django_db_setup):
    data = {
        "name": "testname",
        "email": "test@example.com",
        "password": "strongpassword",
    }
    serializer = UserSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save()
