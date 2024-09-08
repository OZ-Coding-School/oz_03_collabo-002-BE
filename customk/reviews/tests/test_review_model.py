import pytest
from users.models import User
from classes.models import Class
from reviews.models import Review, ReviewImage


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def user(api_client):
    return User.objects.create_user(
        email="testuser@example.com", password="testpassword"
    )


@pytest.fixture
def class_instance():
    return Class.objects.create(title="Test Class")


@pytest.fixture
def review(class_instance, user):
    return Review.objects.create(
        user=user,
        class_id=class_instance,
        review="Test review content",
        rating="4.5",
    )


@pytest.fixture
def review_image(review):
    return ReviewImage.objects.create(
        review=review, image_url="http://example.com/image.jpg"
    )
