import pytest
from django.db import IntegrityError

from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def sample_user():
    """
    User 생성 샘플 코드입니다.
    """
    return User.objects.create(
        name="김민수",
        email="minsu1234@naver.com",
    )


def test_user_create_success():
    """
    유저 모델 생성 성공
    """
    user = User.objects.create(name="kim", email="kim1234@naver.com")
    assert user.email == "kim1234@naver.com"
    assert user.name == "kim"
    assert user.get_username() == "kim1234@naver.com"


def test_user_duplicate_error(sample_user):
    """
    유저 모델 중복 에러
    """
    with pytest.raises(IntegrityError):
        User.objects.create(name="kim", email="minsu1234@naver.com")


def test_user_update_success(sample_user):
    """
    유저 모델 업데이트 성공
    """
    sample_user.name = "Lee"
    sample_user.save()

    updated_user = User.objects.get(id=sample_user.id)
    assert updated_user.name == "Lee"
    assert updated_user.get_username() == "minsu1234@naver.com"
