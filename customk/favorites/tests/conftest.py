import pytest

from classes.models import Class
from classes.tests.conftest import sample_class
from favorites.models import Favorite
from favorites.services import add_favorite_class
from users.tests.conftest import (
    access_token,
    api_client_with_token,
    refresh_token,
    sample_user,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def favorite_instance():
    return Favorite.objects.create(user=sample_user, class_id=sample_class.id)


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
