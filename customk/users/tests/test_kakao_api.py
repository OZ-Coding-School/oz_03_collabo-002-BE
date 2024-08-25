from unittest.mock import patch

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@patch("requests.post")
@patch("requests.get")
def test_callback_success(mock_get, mock_post, api_client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "mock_access_token"}

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "kakao_account": {"email": "test@example.com"},
        "properties": {"nickname": "testuser", "profile_image": "profile-image.url"},
    }

    url = reverse("kakao_callback")
    data = {"code": "mock_authorization_code"}
    response = api_client.post(url, data=data)

    assert response.status_code == 201
    assert response.data["redirect_url"] == "https://naver.com"
