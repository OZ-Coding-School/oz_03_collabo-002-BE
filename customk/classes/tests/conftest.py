import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from classes.models import Class
from users.serializers.user_serializer import UserSerializer


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_class():
    """
    Class 생성 샘플 코드입니다.
    """
    return Class.objects.create(
        title="Sample Class",
        description="This is a sample class",
        max_person=10,
        require_person=5,
        price=50000,
        address="서울시 강남구 테헤란로",
    )


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


@pytest.fixture
def refresh_token(sample_user):
    refresh = RefreshToken.for_user(sample_user)
    return str(refresh)


@pytest.fixture
def access_token(refresh_token):
    return str(RefreshToken(refresh_token).access_token)


@pytest.fixture
def api_client_with_token(sample_user, access_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
    return client
