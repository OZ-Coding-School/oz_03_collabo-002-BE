# ruff: noqa: F811
import pytest
from django.urls import reverse
from rest_framework import status

from classes.tests.conftest import sample_class
from favorites.models import Favorite
from users.tests.conftest import (
    access_token,
    api_client_with_token,
    refresh_token,
    sample_user,
)

pytestmark = pytest.mark.django_db


def test_get_favorites(api_client_with_token, sample_class, favorite_instance):
    url = reverse("favorite")
    response = api_client_with_token.get(url, {"page": 1, "size": 10})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_count"] == 1
    assert len(data["results"]) == 1


def test_post_favorite(api_client_with_token, sample_user, sample_class2):
    url = reverse("favorite") + f"?class_id={sample_class2.id}"
    response = api_client_with_token.post(url, data={})

    assert response.status_code == status.HTTP_201_CREATED


def test_delete_favorite(
    api_client_with_token, sample_user, sample_class, favorite_instance
):
    data, _ = favorite_instance

    url = reverse("favorite") + f"?favorite_id={data.id}"
    response = api_client_with_token.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert (
        Favorite.objects.filter(
            user_id=sample_user.id, class_id=sample_class.id
        ).count()
        == 0
    )
