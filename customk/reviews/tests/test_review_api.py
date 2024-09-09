# ruff: noqa: F811

import pytest
from django.urls import reverse
from rest_framework import status

from .conftest import api_client, review_image, sample_class, sample_user


@pytest.mark.django_db
def test_all_reviews_list(api_client, review, sample_user):
    api_client.force_authenticate(user=sample_user)

    url = reverse("all-reviews")
    response = api_client.get(url, {"page": 1, "size": 10})

    assert response.status_code == status.HTTP_200_OK
    assert "total_count" in response.data
    assert "reviews" in response.data


@pytest.mark.django_db
def test_review_list(api_client, sample_class, review):
    url = reverse("review-list", kwargs={"class_id": sample_class.id})
    response = api_client.get(url, {"page": 1, "size": 10})

    assert response.status_code == status.HTTP_200_OK
    assert "total_count" in response.data
    assert "reviews" in response.data


@pytest.mark.django_db
def test_review_update(api_client, sample_class, review, sample_user):
    api_client.force_authenticate(user=sample_user)

    url = reverse(
        "review-update-delete",
        kwargs={"class_id": sample_class.id, "review_id": review.id},
    )
    data = {"review": "Updated review content", "rating": "5.0"}
    response = api_client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["review"]["review"] == "Updated review content"
    assert response.data["review"]["rating"] == "5.0"


@pytest.mark.django_db
def test_review_delete(api_client, sample_class, review, sample_user):
    api_client.force_authenticate(user=sample_user)

    url = reverse(
        "review-update-delete",
        kwargs={"class_id": sample_class.id, "review_id": review.id},
    )
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_review_image_list(api_client, sample_class, review, review_image):
    url = reverse(
        "review-image-list",
        kwargs={"class_id": sample_class.id, "review_id": review.id},
    )
    response = api_client.get(url, {"page": 1, "size": 10})

    assert response.status_code == status.HTTP_200_OK
    assert "total_count" in response.data
    assert "total_pages" in response.data
    assert "current_page" in response.data
    assert "images" in response.data


@pytest.mark.django_db
def test_photo_review_list(api_client, sample_class, review_image):
    url = reverse("photo-review-list", kwargs={"class_id": sample_class.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "images" in response.data
