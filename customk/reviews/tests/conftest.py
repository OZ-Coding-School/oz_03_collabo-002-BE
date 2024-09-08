import pytest
from rest_framework.test import APIClient

from classes.models import Class
from reviews.models import Review, ReviewImage
from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_user(api_client):
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
def review(sample_class, sample_user):
    return Review.objects.create(
        user=sample_user,
        class_id=sample_class,
        review="Test review content",
        rating="4.5",
    )


@pytest.fixture
def review_image(review):
    return ReviewImage.objects.create(
        review=review, image_url="http://example.com/image.jpg"
    )
