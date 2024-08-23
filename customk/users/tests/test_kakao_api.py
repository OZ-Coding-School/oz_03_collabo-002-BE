from unittest.mock import patch

import pytest
from django.urls import reverse

from users.services.token_service import generate_tokens

pytestmark = pytest.mark.django_db


@patch("requests.post")
@patch("requests.get")
def test_callback_success(mock_get, mock_post, api_client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "mock_access_token"}

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "kakao_account": {"email": "test@example.com"},
        "properties": {"nickname": "testuser"},
    }

    url = reverse("kakao_callback")
    data = {"code": "mock_authorization_code"}
    response = api_client.post(url, data=data)

    assert response.status_code == 201
    assert response.data["redirect_url"] == "https://naver.com"


def test_kakao_logout(api_client, sample_user):
    tokens = generate_tokens(sample_user)

    url = reverse("kakao_logout")

    headers = {"HTTP_KAKAO_CLIENT_ID": "kakao_client_id"}

    api_client.cookies["refresh_token"] = tokens.refresh_token
    api_client.cookies["access_token"] = tokens.access_token
    response = api_client.post(url, **headers)

    assert response.status_code == 200
    assert "https://kauth.kakao.com/oauth/logout" in response.data["kakao_logout_url"]
