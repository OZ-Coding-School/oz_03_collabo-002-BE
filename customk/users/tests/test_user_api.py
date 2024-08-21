import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User
from users.serializers.user_serializer import UserSerializer


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_user(db):
    data = {"name": "testname", "email": "test@example.com", "password": "strongpassword"}
    serializer = UserSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


@pytest.mark.django_db
def test_signup(api_client):
    url = reverse("signup")
    data = {"name": "testname", "email": "test@example.com", "password": "strongpassword"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email="test@example.com").exists()


@pytest.mark.django_db
def test_login(api_client, sample_user):
    url = reverse("login")
    data = {"email": "test@example.com", "password": "strongpassword"}
    response = api_client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_login_failure(api_client):
    url = reverse("login")
    data = {"email": "nonexistent@example.com", "password": "wrongpassword"}
    response = api_client.post(url, data=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_detail(api_client, sample_user):
    user = sample_user
    url = reverse("user-detail")
    api_client.force_authenticate(user=user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == user.email


@pytest.mark.django_db
def test_user_update(api_client, sample_user):
    user = sample_user
    url = reverse("user-detail")
    api_client.force_authenticate(user=user)
    data = {"name": "newtestname"}
    response = api_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.name == "newtestname"


@pytest.mark.django_db
def test_user_delete(api_client, sample_user):
    user = sample_user
    url = reverse("user-detail")
    api_client.force_authenticate(user=user)
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not User.objects.filter(email=user.email).exists()


@pytest.mark.django_db
def test_logout(api_client, sample_user):
    user = sample_user
    url = reverse("logout")
    api_client.force_authenticate(user=user)
    response = api_client.post(url)
    assert response.status_code == status.HTTP_200_OK
