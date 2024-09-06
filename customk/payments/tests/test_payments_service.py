from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from classes.models import ClassDate
from payments.models import ReferralCode
from payments.services import (
    add_class_date_person,
    calculate_refund_amount,
    expire_referral_code,
    minus_class_date_person,
    verify_referral_code,
)

pytestmark = pytest.mark.django_db


def test_add_class_date_person(sample_class):
    class_date = ClassDate.objects.create(
        class_id=sample_class,
        start_date=timezone.now(),
        start_time=timezone.now().time(),
        end_time=timezone.now().time(),
        person=5,
    )
    result = add_class_date_person(class_date.id, 2)
    assert result is True
    class_date.refresh_from_db()
    assert class_date.person == 7


def test_minus_class_date_person(sample_class):
    class_date = ClassDate.objects.create(
        class_id=sample_class,
        start_date=timezone.now(),
        start_time=timezone.now().time(),
        end_time=timezone.now().time(),
        person=5,
    )
    result = minus_class_date_person(class_date.id, 2)
    assert result is True
    class_date.refresh_from_db()
    assert class_date.person == 3


def test_verify_referral_code():
    ReferralCode.objects.create(code="VALIDCODE", discount_rate=10, is_active=True)
    discount_rate = verify_referral_code("VALIDCODE")
    assert discount_rate == "10.00"

    with pytest.raises(ValidationError):
        verify_referral_code("INVALIDCODE")


def test_expire_referral_code():
    referral_code = ReferralCode.objects.create(code="TESTCODE", is_active=True)
    result = expire_referral_code("TESTCODE")
    assert result is True
    referral_code.refresh_from_db()
    assert referral_code.is_active is False

    result = expire_referral_code("NONEXISTENT")
    assert result is False


def test_calculate_refund_amount():
    today = timezone.now().date()
    original_amount = Decimal("100.00")

    # 4일 이상 남은 경우
    start_date = today + timedelta(days=5)
    refund = calculate_refund_amount(start_date, original_amount)
    assert refund == Decimal("100.00")

    # 3일 남은 경우
    start_date = today + timedelta(days=3)
    refund = calculate_refund_amount(start_date, original_amount)
    assert refund == Decimal("50.00")

    # 2일 이하 남은 경우
    start_date = today + timedelta(days=2)
    refund = calculate_refund_amount(start_date, original_amount)
    assert refund == Decimal("0.00")
