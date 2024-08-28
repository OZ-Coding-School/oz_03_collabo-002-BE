import base64
import mimetypes
import os
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from users.models import User

pytestmark = pytest.mark.django_db


def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            mime_type, _ = mimetypes.guess_type(image_path)
            return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        print(f"Error: 파일을 찾을 수 없습니다. 경로를 확인하세요: {image_path}")
        return None


def test_signup(api_client):
    url = reverse("signup")
    base_dir = os.path.dirname(__file__)
    image_path = os.path.join(base_dir, "testimage.png")

    image_base64_str = encode_image_to_base64(image_path)
    data = {
        "name": "testname",
        "email": "testsign@example.com",
        "password": "strongpassword",
        "profile_image": image_base64_str,
    }

    with patch(
        "common.services.ncp_api_conf.ObjectStorage.put_object"
    ) as mock_put_object:
        mock_put_object.return_value = (
            200,
            "https://mock-storage-url.com/profile-images/testimage.png",
        )

        response = api_client.post(url, data)
        print(response.data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="testsign@example.com").exists()

        mock_put_object.assert_called_once()


def test_login(api_client, sample_user):
    url = reverse("login")
    data = {"email": "test@example.com", "password": "strongpassword"}
    response = api_client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == sample_user.name


def test_login_failure(api_client):
    url = reverse("login")
    data = {"email": "nonexistent@example.com", "password": "wrongpassword"}
    response = api_client.post(url, data=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_detail(api_client, sample_user):
    user = sample_user
    url = reverse("user-detail")
    api_client.force_authenticate(user=user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == user.email


def test_user_update(api_client, sample_user):
    user = sample_user
    url = reverse("user-detail")
    api_client.force_authenticate(user=user)
    data = {"name": "newtestname"}
    response = api_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.name == "newtestname"


def test_user_delete(api_client, sample_user):
    user = sample_user
    url = reverse("user-detail")
    api_client.force_authenticate(user=user)
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not User.objects.filter(email=user.email).exists()


def test_logout(api_client, sample_user):
    user = sample_user
    url = reverse("logout")
    api_client.force_authenticate(user=user)
    response = api_client.post(url)
    assert response.status_code == status.HTTP_200_OK
