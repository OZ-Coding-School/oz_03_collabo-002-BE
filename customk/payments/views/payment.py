from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from payments.serializers import BasePaymentSerializer, PaymentPostAPISerializer
from payments.services import get_payment_datas


class PaymentView(APIView):
    @extend_schema(
        methods=["GET"],
        summary="결제 목록 조회",
        description="유저가 결제한 목록을 페이지네이션형태로 가져옵니다",
        parameters=[
            OpenApiParameter(
                name="page",
                description="페이지",
                required=False,
                default=1,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="size",
                description="사이즈",
                required=False,
                default=10,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: inline_serializer(
                name="PaymentListSerializer",
                fields={
                    "total_count": serializers.IntegerField(),
                    "total_pages": serializers.IntegerField(),
                    "current_page": serializers.IntegerField(),
                    "results": BasePaymentSerializer(many=True),
                },
            ),
            400: OpenApiResponse(description="Page input error"),
        },
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        page = int(request.GET.get("page", "1"))
        size = int(request.GET.get("size", "10"))
        offset = (page - 1) * size

        user = request.user

        if page < 1:
            return Response("page input error", status=status.HTTP_400_BAD_REQUEST)

        total_count, total_pages, payments = get_payment_datas(user.id, offset, size)

        serializer = BasePaymentSerializer(payments, many=True)

        return Response(
            {
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        methods=["POST"],
        summary="결제 생성",
        description="결제데이터를 생성하는 API",
        request=PaymentPostAPISerializer,
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = PaymentPostAPISerializer(
            data=request.data, context={"payer_email": request.user.email,
                                        "user_id": request.user.id}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "COMPLETED",
                    "product_data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        methods=["DELETE"],
        summary="결제 데이터 삭제",
        description="결제 한 데이터를 삭제하는 API",
        parameters=[
            OpenApiParameter(
                name="payment_id",
                description="삭제할 결제 데이터 id",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            )
        ],
        request=None,
        responses={
            204: OpenApiResponse(description="결제 데이터 삭제 성공"),
            400: OpenApiResponse(description="payment_id is required"),
        },
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        payment_id = int(request.GET.get("payment_id", 0))

        if payment_id == 0:
            return Response(
                {"error": "class_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        Payment.objects.filter(id=payment_id).delete()

        return Response(
            {"message": "success delete"}, status=status.HTTP_204_NO_CONTENT
        )
