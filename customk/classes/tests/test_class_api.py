import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
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
def test_class_create(api_client_with_token):
    url = reverse("class-list")
    data = {
        "title": "Test Class",
        "description": "Test class description",
        "max_person": 10,
        "require_person": 5,
        "price": 50000,
        "address": "성남시 중원구 희망로",
    }
    response = api_client_with_token.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == "success"
    assert Class.objects.filter(title="Test Class").exists()


@pytest.mark.django_db
def test_class_delete(api_client_with_token, sample_class):
    url = reverse("class-list")
    data = {"id": sample_class.id}
    response = api_client_with_token.delete(url, data, format="json")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Class.objects.filter(id=sample_class.id).exists()


@pytest.mark.django_db
def test_classes_view_queries(api_client_with_token):
    url = reverse("class-list")

    with CaptureQueriesContext(connection) as ctx:
        response = api_client_with_token.get(url)

    assert response.status_code == 200

    for query in ctx.captured_queries:
        print(query["sql"])

    # 발생한 쿼리 수를 확인
    print(f"Total queries: {len(ctx.captured_queries)}")
    assert len(ctx.captured_queries) <= 9
