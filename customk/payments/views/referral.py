from django.core.exceptions import ValidationError
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.services import verify_referral_code


class ReferralView(APIView):
    @extend_schema(
        summary="추천인 코드 검증",
        description="사용자가 제공한 추천인 코드를 검증하고, 해당 코드가 유효하면 관련 할인율 데이터를 반환합니다.",
        parameters=[
            OpenApiParameter(
                name="code",
                description="추천인 코드 (예: BD4CFEG)",
                location=OpenApiParameter.QUERY,
                required=True,
                type=str,
            ),
        ],
        responses={
            200: inline_serializer(
                name="ReferralResponseSerializer",
                fields={
                    "discount_rate": serializers.IntegerField(
                        help_text="할인율 (0~100 백분율)"
                    ),
                },
            ),
            400: inline_serializer(
                name="ErrorResponseSerializer",
                fields={
                    "error": serializers.CharField(
                        help_text="유효하지 않은 추천인 코드"
                    ),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Valid Referral Code",
                value={"discount_rate": 15.0},
                response_only=True,
                status_codes=[status.HTTP_200_OK],
            ),
            OpenApiExample(
                "Invalid Referral Code",
                value={"error": "유효하지 않은 추천인 코드입니다"},
                response_only=True,
                status_codes=[status.HTTP_400_BAD_REQUEST],
            ),
        ],
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        code = request.GET.get("code", "")
        try:
            discount_rate = verify_referral_code(code)
            return Response({"discount_rate": discount_rate}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
