from typing import Any

from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Reaction, Review


class ReactToReviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["POST"],
        summary="리뷰에 반응 추가",
        description="사용자가 리뷰에 대해 좋아요 또는 싫어요를 추가하는 API입니다. 'review_id'는 쿼리 파라미터로 제공해야 합니다.",
        parameters=[
            OpenApiParameter(
                name="class_id",
                description="클래스 ID",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="review_id",
                description="리뷰 ID",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ],
        request=None,
        responses={
            200: OpenApiResponse(description="리뷰 반응 추가 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="리뷰를 찾을 수 없음"),
        },
    )
    def post(
        self, request: Request, class_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        review_id = request.query_params.get("review_id")

        if review_id is None:
            return Response(
                {"status": "error", "message": "리뷰 ID가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review = get_object_or_404(Review, pk=review_id)
        user = request.user

        if not user.is_authenticated:
            return Response(
                {
                    "status": "error",
                    "message": "인증된 사용자만 반응을 추가할 수 있습니다.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            reaction_type = int(request.data.get("reaction", Reaction.NO_REACTION))
        except ValueError:
            return Response(
                {"status": "error", "message": "잘못된 반응 값입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        reaction, created = Reaction.objects.get_or_create(user=user, review=review)
        reaction.reaction = reaction_type
        reaction.save()

        reactions = Reaction.get_review_reactions(review)
        response_data = {
            "status": "success",
            "message": "리뷰 반응이 성공적으로 추가되었습니다.",
            "data": reactions,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        methods=["PATCH"],
        summary="리뷰에 대한 반응 수정 또는 삭제",
        description="사용자가 리뷰에 대한 반응을 수정하거나 삭제하는 API입니다. '삭제'를 위해 반응 값을 'NO_REACTION'으로 설정합니다.",
        parameters=[
            OpenApiParameter(
                name="class_id",
                description="클래스 ID",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="review_id",
                description="리뷰 ID",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ],
        request=None,
        responses={
            200: OpenApiResponse(description="리뷰 반응 수정 또는 삭제 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="반응 또는 리뷰를 찾을 수 없음"),
        },
    )
    def patch(
        self, request: Request, class_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        review_id = request.query_params.get("review_id")
        if review_id is None:
            return Response(
                {"status": "error", "message": "리뷰 ID가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review = get_object_or_404(Review, pk=review_id)
        user = request.user

        if not user.is_authenticated:
            return Response(
                {
                    "status": "error",
                    "message": "인증된 사용자만 반응을 수정할 수 있습니다.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            reaction_type = int(request.data.get("reaction", Reaction.NO_REACTION))
        except ValueError:
            return Response(
                {"status": "error", "message": "잘못된 반응 값입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reaction = Reaction.objects.get(user=user, review=review)
            reaction.reaction = reaction_type
            reaction.save()

            reactions = Reaction.get_review_reactions(review)
            response_data = {
                "status": "success",
                "message": "리뷰 반응이 성공적으로 수정/삭제되었습니다.",
                "data": reactions,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Reaction.DoesNotExist:
            return Response(
                {"status": "error", "message": "리뷰에 대한 반응이 존재하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
