import pytest
from django.urls import reverse
from rest_framework import status

from classes.models import Class


@pytest.mark.django_db
def test_class_list(api_client):
    url = reverse("class-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "success"
    assert isinstance(response.data["data"], list)


@pytest.mark.django_db
def test_class_create(api_client):
    url = reverse("class-list")
    data = {
        "title": "Test Class",
        "description": "Test class description",
        "max_person": 10,
        "require_person": 5,
        "price": 50000,
        "address": {"state": "Seoul", "city": "Gangnam", "street": "Teheran-ro"},
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == "success"
    assert Class.objects.filter(title="Test Class").exists()


@pytest.mark.django_db
def test_class_delete(api_client, sample_class):
    url = reverse("class-list")
    data = {"id": sample_class.id}
    response = api_client.delete(url, data, format="json")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Class.objects.filter(id=sample_class.id).exists()
