from django.shortcuts import get_object_or_404, render
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classes.models import Class
from reactions.models import Reaction
from reviews.models import Review
from reviews.serializers import ReviewSerializer


class ReviewListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        summary="리뷰 목록 조회",
        description="특정 클래스에 대한 리뷰 목록을 조회하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id", description="클래스 ID", required=True, type=int
            )
        ],
        responses={
            200: OpenApiResponse(
                description="리뷰 목록 조회 성공",
                response=inline_serializer(
                    name="ReviewListResponse",
                    fields={
                        "reviews": serializers.ListSerializer(
                            child=inline_serializer(
                                name="ReviewData",
                                fields={
                                    "review": ReviewSerializer(),
                                    "likes_count": serializers.IntegerField(),
                                    "dislikes_count": serializers.IntegerField(),
                                },
                            )
                        )
                    },
                ),
            ),
            404: OpenApiResponse(description="리뷰를 찾을 수 없음"),
        },
    )
    def get(self, request, class_id, *args, **kwargs):
        class_id = Class.objects.get(id=class_id)

        reviews = Review.objects.filter(class_id=class_id)

        if not reviews.exists():
            return Response({"message": "No reviews found for this class."}, status=404)

        review_data = []
        for review in reviews:
            reactions = Reaction.get_review_reactions(review)
            review_data.append(
                {
                    "review": ReviewSerializer(review).data,
                    "likes_count": reactions["likes_count"],
                    "dislikes_count": reactions["dislikes_count"],
                }
            )

        response_data = {
            "reviews": review_data,
        }
        return Response(response_data, status=200)

    @extend_schema(
        methods=["POST"],
        summary="리뷰 생성",
        description="특정 클래스에 대해 새 리뷰를 생성하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id", description="클래스 ID", required=True, type=int
            )
        ],
        request=ReviewSerializer,
        responses={
            201: OpenApiResponse(
                description="리뷰 생성 성공",
                response=inline_serializer(
                    name="ReviewCreateResponse",
                    fields={
                        "message": serializers.CharField(),
                        "review": ReviewSerializer(),
                    },
                ),
            ),
            400: OpenApiResponse(description="잘못된 요청"),
        },
    )
    def post(self, request, class_id, *args, **kwargs):
        try:
            class_id = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"class_id": "Invalid class ID."}, status=400)

        data = request.data.copy()
        data["user"] = request.user.id
        data["class_id"] = class_id.id

        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user, class_id=class_id)
            return Response(
                {"message": "Review successfully created.", "review": serializer.data},
                status=201,
            )

        return Response(serializer.errors, status=400)

    @extend_schema(
        methods=["PATCH"],
        summary="리뷰 업데이트",
        description="특정 리뷰를 업데이트하는 API입니다.",
        request=ReviewSerializer,
        responses={
            200: OpenApiResponse(
                description="리뷰 업데이트 성공",
                response=inline_serializer(
                    name="ReviewUpdateResponse",
                    fields={
                        "message": serializers.CharField(),
                        "review": ReviewSerializer(),
                    },
                ),
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="리뷰를 찾을 수 없음"),
        },
    )
    def patch(self, request, class_id, *args, **kwargs):
        review_id = request.data.get("id")

        if not review_id:
            return Response({"error": "Review ID is required for update."}, status=400)

        review = get_object_or_404(Review, id=review_id, class_id=class_id)

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Review successfully updated.", "review": serializer.data},
                status=200,
            )

        return Response(serializer.errors, status=400)


class ReviewDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["DELETE"],
        summary="리뷰 삭제",
        description="특정 리뷰를 삭제하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id", description="클래스 ID", required=True, type=int
            ),
            OpenApiParameter(
                name="review_id", description="리뷰 ID", required=True, type=int
            ),
        ],
        responses={
            204: OpenApiResponse(description="리뷰 삭제 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="리뷰를 찾을 수 없음"),
        },
    )
    def delete(self, request, class_id, review_id, *args, **kwargs):
        review = get_object_or_404(Review, id=review_id, class_id=class_id)
        review.delete()

        return Response({"message": "Review successfully deleted."}, status=204)
