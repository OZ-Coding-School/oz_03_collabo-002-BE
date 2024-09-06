# ruff: noqa: F811
import pytest
from django.utils import timezone

from classes.models import ClassDate
from classes.tests.conftest import (
    access_token,
    api_client_with_token,
    refresh_token,
    sample_class,
    sample_user,
)
from payments.serializers import PaymentPostAPISerializer


@pytest.fixture
def create_class_date(sample_class):
    class_date = ClassDate.objects.create(
        class_id=sample_class,
        start_date=timezone.now(),
        start_time=timezone.now().time(),
        end_time=timezone.now().time(),
        person=5,
    )

    return class_date


@pytest.fixture
def create_payment(sample_user, sample_class, create_class_date):
    data = {
        "class_id": sample_class.id,
        "quantity": "1",
        "options": "김치 만들기",
        "class_date_id": create_class_date.id,
        "amount": 100.32,
    }

    serializer = PaymentPostAPISerializer(
        data=data,
        context={"payer_email": sample_user.email},  # type: ignore
    )
    if serializer.is_valid():
        serializer.save(user_id=sample_user.id)
