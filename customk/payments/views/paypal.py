import logging
import os
from decimal import Decimal

import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from payments.serializers import PaymentPayPalSerializer
from payments.services import generate_access_token

logger = logging.getLogger(__name__)

PAYPAL_API_URL = os.environ.get("PAYPAL_API_URL")


@api_view(["POST"])
@permission_classes([AllowAny])
def create_order(request: Request) -> Response:
    logger.info("Creating paypal payment")
    amount = Decimal(str(request.data.get("amount", "0")))

    access_token = generate_access_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.post(
        f"{PAYPAL_API_URL}/v2/checkout/orders",
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {"amount": {"currency_code": "USD", "value": str(amount)}}
            ],
        },
        headers=headers,
    )

    return Response(response.json(), status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def capture_order(request: Request, order_id: str) -> Response:
    logger.info("Capture paypal payment")

    access_token = generate_access_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    serializer = PaymentPayPalSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    response = requests.post(
        f"{PAYPAL_API_URL}/v2/checkout/orders/{order_id}/capture", headers=headers
    )

    capture_data = response.json()

    serializer = PaymentPayPalSerializer(
        data=request.data, context={"paypal_data": capture_data}
    )
    serializer.is_valid(raise_exception=True)

    if capture_data.get("status") != "COMPLETED":
        logger.warning("status not completed")
        response = Response(capture_data, status=status.HTTP_400_BAD_REQUEST)
        return response

    if not capture_data:
        logger.warning("not capture data")
        return Response(
            {"error": "Failed to capture PayPal payment"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer.save(user_id=request.user.id)

    return Response(
        {
            "capture_data": capture_data,
            "status": "COMPLETED",
            "product_data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )
