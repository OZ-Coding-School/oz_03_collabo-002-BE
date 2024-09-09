import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_all_questions_list(api_client, sample_user, question):
    api_client.force_authenticate(user=sample_user)

    url = reverse("all-questions")
    response = api_client.get(url, {"page": 1, "size": 10})

    assert response.status_code == status.HTTP_200_OK
    assert "total_count" in response.data
    assert "questions" in response.data


@pytest.mark.django_db
def test_question_list(api_client, sample_user, sample_class, question):
    api_client.force_authenticate(user=sample_user)

    url = reverse("class-question-list", kwargs={"class_id": sample_class.id})
    response = api_client.get(url, {"page": 1, "size": 10})

    assert response.status_code == status.HTTP_200_OK
    assert "total_count" in response.data
    assert "questions" in response.data


@pytest.mark.django_db
def test_question_create(api_client, sample_user, sample_class):
    api_client.force_authenticate(user=sample_user)

    url = reverse("class-question-list", kwargs={"class_id": sample_class.id})
    data = {"question": "New test question", "question_title": "New question title"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == "success"
    assert response.data["message"] == "Question or Answer submitted successfully"


@pytest.mark.django_db
def test_question_update(api_client, sample_user, sample_class, question):
    api_client.force_authenticate(user=sample_user)

    url = reverse("class-question-list", kwargs={"class_id": sample_class.id})
    data = {
        "question": "Updated test question",
        "question_title": "Updated question title",
    }
    response = api_client.patch(f"{url}?question_id={question.id}", data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "success"
    assert response.data["message"] == "Question or Answer updated successfully"
    assert response.data["data"]["question"] == "Updated test question"


@pytest.mark.django_db
def test_question_delete(api_client, sample_user, sample_class, question):
    api_client.force_authenticate(user=sample_user)

    url = reverse("class-question-list", kwargs={"class_id": sample_class.id})
    response = api_client.delete(f"{url}?question_id={question.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "success"
    assert response.data["message"] == "Question or Answer deleted successfully"
