import logging
import os
from decimal import Decimal

import requests
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from classes.models import ClassDate
from common.serializers import ErrorResponseSerializer
from payments.models import Payment
from payments.serializers import (
    PaymentPayPalSerializer,
    RefundSuccessResponseSerializer,
)
from payments.services import (
    calculate_refund_amount,
    generate_access_token,
    minus_class_date_person,
)

logger = logging.getLogger(__name__)

PAYPAL_API_URL = os.environ.get("PAYPAL_API_URL")


@extend_schema(
    methods=["POST"],
    summary="Paypal 오더 생성 POST",
    description="생성 성공 시 onApprove 함수로 콜백합니다",
    request=inline_serializer(
        name="CreateOrderSerializer",
        fields={
            "amount": serializers.CharField(help_text="상품 가격"),
        },
    ),
    responses={
        200: OpenApiResponse(description="onApprove로 콜백합니다."),
        500: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            "서버 에러",
            value={"error": "failed to create order: {error message}"},
            response_only=True,
            status_codes=[status.HTTP_500_INTERNAL_SERVER_ERROR],
        )
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def create_order(request: Request) -> Response:
    logger.info("Creating paypal payment")
    try:
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

    except Exception as e:
        logger.warning(f"failed to create order {str(e)}")
        return Response(
            {"message": "failed to create order", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    methods=["POST"],
    summary="Paypal Capture Order POST",
    description="결제 API 완료하면, 결제내역이 생성됩니다.",
    request=PaymentPayPalSerializer,
    responses={
        200: inline_serializer(
            name="capture order serializer",
            fields={
                "capture_data": serializers.JSONField(),
                "status": serializers.CharField(),
            },
        ),
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "서버 에러",
            value={"error": "failed to caputre order: {error message}"},
            response_only=True,
            status_codes=[status.HTTP_500_INTERNAL_SERVER_ERROR],
        ),
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def capture_order(request: Request, order_id: str) -> Response:
    logger.info("Capture paypal payment")
    try:
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
            return Response(capture_data, status=status.HTTP_400_BAD_REQUEST)

        if not capture_data:
            logger.warning("not capture data")
            return Response(
                {"error": "Failed to capture PayPal payment"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        logger.info(f"{request.user.id}, user id is it ?")
        serializer.save(user_id=4)

        return Response(
            {
                "capture_data": capture_data,
                "status": "COMPLETED",
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.warning(f"failed to create order {str(e)}")
        return Response(
            {"message": "failed to capture order", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    methods=["POST"],
    parameters=[
        OpenApiParameter(
            name="payment_id",
            description="취소할 결제내역 id",
            required=True,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
        )
    ],
    request=None,
    responses={
        200: RefundSuccessResponseSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
    description="주문에 대한 환불을 처리합니다. 환불 금액은 클래스 시작일까지 남은 기간에 따라 계산됩니다.",
    summary="주문 환불 처리",
    examples=[
        OpenApiExample(
            "Successful Refund",
            description="전액 환불의 예",
            value={
                "message": "환불이 성공적으로 처리되었습니다.",
                "refund_amount": "100.00",
            },
            response_only=True,
            status_codes=["200"],
        ),
        OpenApiExample(
            "Partial Refund",
            description="부분 환불의 예",
            value={
                "message": "환불이 성공적으로 처리되었습니다.",
                "refund_amount": "50.00",
            },
            response_only=True,
            status_codes=["200"],
        ),
        OpenApiExample(
            "Refund Not Possible",
            description="환불 불가능한 경우의 예",
            value={"error": "환불이 불가능합니다."},
            response_only=True,
            status_codes=["400"],
        ),
    ],
    tags=["결제"],
)
@api_view(["POST"])
def refund_order(request: Request, payment_id: int) -> Response:
    try:
        payment = Payment.objects.get(id=payment_id)

        class_date = ClassDate.objects.get(id=payment.class_date_id)

        refund_amount = calculate_refund_amount(class_date.start_date, payment.amount)

        if refund_amount == 0:
            return Response(
                {"error": "환불이 불가능합니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        access_token = generate_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        payload = {
            "amount": {"value": str(refund_amount), "currency_code": payment.currency}
        }
        response = requests.post(
            f"{PAYPAL_API_URL}/v2/payments/captures/{payment.capture_id}/refund",
            json=payload,
            headers=headers,
        )

        if response.status_code == 201:
            payment.status = "REFUNDED"
            payment.refunded_amount = refund_amount
            minus_class_date_person(payment.class_date_id, payment.quantity)
            payment.save()
            return Response(
                {
                    "message": "환불이 성공적으로 처리되었습니다.",
                    "refund_amount": refund_amount,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "error": "환불 처리 중 오류가 발생했습니다.",
                    "details": response.json(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Payment.DoesNotExist:
        return Response(
            {"error": "해당 결제 정보를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ClassDate.DoesNotExist:
        return Response(
            {"error": "해당 클래스 날짜 정보를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
