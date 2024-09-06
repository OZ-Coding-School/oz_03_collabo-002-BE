import pytest
from django.urls import reverse
from rest_framework import status

from payments.models import ReferralCode

pytestmark = pytest.mark.django_db


def test_valid_referral_code(api_client_with_token):
    ReferralCode.objects.create(code="VALIDCODE", discount_rate=10, is_active=True)
    url = reverse("referral-view") + "?code=VALIDCODE"
    response = api_client_with_token.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"discount_rate": "10.00"}


def test_invalid_referral_code(api_client_with_token):
    url = reverse("referral-view") + "?code=INVALIDCODE"
    response = api_client_with_token.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


def test_get_payments(
    sample_class, sample_user, create_class_date, create_payment, api_client_with_token
):
    url = reverse("payments-view")
    response = api_client_with_token.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "total_count" in response.data
    assert "total_pages" in response.data
    assert "current_page" in response.data
    assert "results" in response.data


def test_create_payment(api_client_with_token, create_class_date, sample_class):
    url = reverse("payments-view")
    data = {
        "class_id": sample_class.id,
        "quantity": "1",
        "class_date_id": create_class_date.id,
        "amount": 100.32,
    }
    response = api_client_with_token.post(url, data=data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["message"] == "success create payment"
    assert response.data["status"] == "COMPLETED"


def test_invalid_payment_data(api_client_with_token):
    url = reverse("payments-view")
    data = {}
    response = api_client_with_token.post(url, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
