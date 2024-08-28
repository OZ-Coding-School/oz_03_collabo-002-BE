import pytest
from rest_framework.test import APIClient

from classes.models import Class


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_class():
    """
    Class 생성 샘플 코드입니다.
    """
    return Class.objects.create(
        title="Sample Class",
        description="This is a sample class",
        max_person=10,
        require_person=5,
        price=50000,
        address={"state": "Seoul", "city": "Gangnam", "street": "Teheran-ro"},
    )
