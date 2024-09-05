import base64
import logging
import os

import requests

from django.core.exceptions import ObjectDoesNotExist
from classes.models import Class, ClassDate
from payments.models import Payment, ReferralCode

logger = logging.getLogger(__name__)


def generate_access_token() -> str | None:
    logger.info("Generating access token")
    client_id = os.environ.get("PAYPAL_CLIENT_ID")
    secret_id = os.environ.get("PAYPAL_SECRET_ID")
    paypal_api_url = os.environ.get("PAYPAL_API_URL")

    if not client_id or not secret_id:
        raise ValueError("MISSING_API_CREDENTIALS")

    auth = base64.b64encode(f"{client_id}:{secret_id}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"grant_type": "client_credentials"}

    try:
        response = requests.post(
            f"{paypal_api_url}/v1/oauth2/token", headers=headers, data=data
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.RequestException as error:
        print(f"Failed to generate Access Token: {error}")
        return None


def get_payment_datas(user_id: int, offset: int, size: int):
    logger.info("get payment datas")
    payments_query = Payment.objects.filter(user_id=user_id).order_by("-id")

    class_ids = payments_query.values_list("class_id", flat=True).distinct()
    class_date_ids = payments_query.values_list("class_date_id", flat=True).distinct()

    classes = Class.objects.filter(id__in=class_ids)
    class_dates = ClassDate.objects.filter(id__in=class_date_ids)

    class_dict = {c.id: c for c in classes}
    class_date_dict = {cd.id: cd for cd in class_dates}

    total_count = payments_query.count()
    total_pages = (total_count // size) + 1

    payments = payments_query[offset : offset + size]

    for payment in payments:
        payment.related_class = class_dict.get(payment.class_id)
        payment.related_class_date = class_date_dict.get(payment.class_date_id)

    return total_count, total_pages, payments


def add_class_date_person(class_date_id, person) -> bool:
    try:
        class_date = ClassDate.objects.select_for_update().get(id=class_date_id)
        class_date.person += person
        class_date.save()
        return True
    except ObjectDoesNotExist:
        return False


def minus_class_date_person(class_date_id, person) -> bool:
    try:
        class_date = ClassDate.objects.select_for_update().get(id=class_date_id)
        if class_date.person > 0:
            class_date.person -= person
            class_date.save()
        return True
    except ObjectDoesNotExist:
        return False


def verify_referral_code(code: str) -> str:
    try:
        referral_code = ReferralCode.objects.get(code=code, is_active=True)
        return str(referral_code.discount_rate)
    except ObjectDoesNotExist:
        return None


def expire_referral_code(code: str) -> bool:
    try:
        referral_code = ReferralCode.objects.select_for_update().get(code=code)
        referral_code.is_active = False
        referral_code.save()
        return True
    except ObjectDoesNotExist:
        return False
