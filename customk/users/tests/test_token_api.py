import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestCustomTokenRefreshView:
    def test_refresh_token_success(self, api_client, refresh_token):
        api_client.cookies["refresh_token"] = refresh_token
        url = reverse("token_refresh")
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert "access" not in response.data
        assert "refresh" not in response.data
        assert "access_token" in response.cookies

    def test_refresh_token_missing(self, api_client):
        url = reverse("token_refresh")
        response = api_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Refresh token not found in cookies."

    def test_refresh_token_invalid(self, api_client):
        api_client.cookies["refresh_token"] = "invalid_token"
        url = reverse("token_refresh")
        response = api_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid refresh token."


class TestCustomTokenVerifyView:
    def test_verify_token_success(self, api_client, access_token):
        api_client.cookies["access_token"] = access_token
        url = reverse("token_verify")
        response = api_client.post(url)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Token is valid"

    def test_verify_token_missing(self, api_client):
        url = reverse("token_verify")
        response = api_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Access token not found in cookies."

    def test_verify_token_invalid(self, api_client):
        api_client.cookies["access_token"] = "invalid_token"
        url = reverse("token_verify")
        response = api_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Token is invalid or expired"
