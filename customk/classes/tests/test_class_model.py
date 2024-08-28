import pytest
from django.db import IntegrityError

from classes.models import Class

pytestmark = pytest.mark.django_db


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
        address={"state": "서울", "city": "강남구", "street": "테헤란로"},
    )


def test_class_create_success():
    """
    클래스 모델 생성 성공
    """
    class_instance = Class.objects.create(
        title="New Class",
        description="Description of new class",
        max_person=20,
        require_person=10,
        price=60000,
        address={"state": "서울", "city": "강남구", "street": "테헤란로"},
    )
    assert class_instance.title == "New Class"
    assert class_instance.description == "Description of new class"
    assert class_instance.max_person == 20
    assert class_instance.require_person == 10
    assert class_instance.price == 60000
    assert class_instance.address == {
        "state": "서울",
        "city": "강남구",
        "street": "테헤란로",
    }


def test_class_update_success(sample_class):
    sample_class.title = "Updated Class Title"
    sample_class.save()

    updated_class = Class.objects.get(id=sample_class.id)
    assert updated_class.title == "Updated Class Title"
    assert updated_class.description == "This is a sample class"
    assert updated_class.max_person == 10
    assert updated_class.require_person == 5
    assert updated_class.price == 50000
    assert updated_class.address == {
        "state": "서울",
        "city": "강남구",
        "street": "테헤란로",
    }
