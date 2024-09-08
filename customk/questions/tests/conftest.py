import pytest
from rest_framework.test import APIClient

from classes.models import Class
from questions.models import Question
from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_user():
    return User.objects.create_user(
        email="testuser@example.com", password="testpassword"
    )


@pytest.fixture
def sample_class():
    return Class.objects.create(
        title="Sample Class",
        description="This is a sample class",
        max_person=10,
        require_person=5,
        price=50000,
        address="서울시 강남구 테헤란로",
    )


@pytest.fixture
def question(sample_user, sample_class):
    return Question.objects.create(
        user_id=sample_user,
        class_id=sample_class,
        question="Test question content",
        question_title="Test question title",
    )
