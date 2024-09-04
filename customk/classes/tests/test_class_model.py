import pytest

from classes.models import Category, Class

pytestmark = pytest.mark.django_db


@pytest.fixture
def class_instance():
    category = Category.objects.create(name="Sample Category")

    return Class.objects.create(
        title="Sample Class",
        description="A sample class instance for testing",
        max_person=10,
        require_person=5,
        price=1000,
        address="Seoul, Gangnam-gu",
        class_type=["Online", "Offline"],  # JSONField로 리스트 형식의 데이터
        category=category,
        discount_rate=10,
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
        address="서울시 강남구 테헤란로",
    )
    assert class_instance.title == "New Class"
    assert class_instance.description == "Description of new class"
    assert class_instance.max_person == 20
    assert class_instance.require_person == 10
    assert class_instance.price == 60000
    assert class_instance.address == "서울시 강남구 테헤란로"


def test_class_update_success(class_instance):
    class_instance.title = "Updated Class Title"
    class_instance.save()

    updated_class = Class.objects.get(id=class_instance.id)
    assert updated_class.title == "Updated Class Title"
    assert updated_class.description == "A sample class instance for testing"
    assert updated_class.max_person == 10
    assert updated_class.require_person == 5
    assert updated_class.price == 1000
    assert updated_class.address == "Seoul, Gangnam-gu"
