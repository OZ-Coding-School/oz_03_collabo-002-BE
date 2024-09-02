import pytest

from classes.models import Class
from favorites.services import add_favorite_class

pytestmark = pytest.mark.django_db


@pytest.fixture
def favorite_instance(sample_user, sample_class):
    return add_favorite_class(user_id=sample_user.id, class_id=sample_class.id)


@pytest.fixture
def sample_class2():
    return Class.objects.create(
        title="Sample Class2",
        description="This is a sample class2",
        max_person=100,
        require_person=50,
        price=50000,
        address={"state": "Seoul", "city": "Gangnam", "street": "Teheran-ro"},
    )
