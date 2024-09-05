from typing import Any, Dict, Optional, Tuple

from django.shortcuts import get_object_or_404, render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from classes.models import Class
from reactions.models import Reaction
from reviews.models import Review
from reviews.serializers import ReviewSerializer

from .models import ReviewImage
from .serializers import ReviewImageSerializer


class AllReviewsListView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

    @extend_schema(
        methods=["GET"],
        summary="전체 리뷰 목록 조회",
        description="전체 리뷰 목록을 페이지네이션 형태로 조회하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="page",
                description="페이지 번호",
                required=False,
                default=1,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="size",
                description="페이지당 항목 수",
                required=False,
                default=15,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="리뷰 목록 조회 성공",
                response=inline_serializer(
                    name="AllReviewListResponse",
                    fields={
                        "total_count": serializers.IntegerField(
                            help_text="전체 리뷰 수"
                        ),
                        "total_pages": serializers.IntegerField(
                            help_text="전체 페이지 수"
                        ),
                        "current_page": serializers.IntegerField(
                            help_text="현재 페이지 번호"
                        ),
                        "reviews": serializers.ListSerializer(
                            child=inline_serializer(
                                name="AllReviewData",
                                fields={
                                    "review": inline_serializer(
                                        name="AllReviewDetail",
                                        fields={
                                            **ReviewSerializer().fields,
                                            "likes_count": serializers.IntegerField(
                                                help_text="해당 리뷰의 좋아요 수"
                                            ),
                                        },
                                    ),
                                },
                            ),
                            help_text="리뷰 목록",
                        ),
                    },
                ),
            ),
            400: OpenApiResponse(description="잘못된 페이지 번호 입력"),
        },
    )
    def get(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        page = int(request.GET.get("page", "1"))
        size = int(request.GET.get("size", "15"))
        offset = (page - 1) * size

        if page < 1:
            return Response("Page input error", status=400)

        reviews = Review.objects.all()
        total_count = reviews.count()
        total_pages = (total_count // size) + (1 if total_count % size > 0 else 0)

        reviews = reviews.order_by("-id")[offset : offset + size]

        review_data = []
        for review in reviews:
            reactions = Reaction.get_review_reactions(review)
            review_data.append(
                {
                    "review": {
                        **ReviewSerializer(review).data,
                        "likes_count": reactions["likes_count"],
                    }
                }
            )

        response_data = {
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "reviews": review_data,
        }
        return Response(response_data, status=200)


class ReviewListView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        methods=["GET"],
        summary="리뷰 목록 조회",
        description="특정 클래스에 대한 리뷰 목록을 페이지네이션 형태로 조회하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id",
                description="클래스 ID",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="page",
                description="페이지 번호",
                required=False,
                default=1,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="size",
                description="페이지당 항목 수",
                required=False,
                default=15,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="리뷰 목록 조회 성공",
                response=inline_serializer(
                    name="ReviewListResponse",
                    fields={
                        "total_count": serializers.IntegerField(
                            help_text="전체 리뷰 수"
                        ),
                        "total_pages": serializers.IntegerField(
                            help_text="전체 페이지 수"
                        ),
                        "current_page": serializers.IntegerField(
                            help_text="현재 페이지 번호"
                        ),
                        "reviews": serializers.ListSerializer(
                            child=inline_serializer(
                                name="ReviewData",
                                fields={
                                    "review": inline_serializer(
                                        name="ReviewDetail",
                                        fields={
                                            **ReviewSerializer().fields,
                                            "likes_count": serializers.IntegerField(
                                                help_text="해당 리뷰의 좋아요 수"
                                            ),
                                        },
                                    ),
                                },
                            ),
                            help_text="리뷰 목록",
                        ),
                    },
                ),
            ),
            400: OpenApiResponse(description="잘못된 페이지 번호 입력"),
            404: OpenApiResponse(description="리뷰를 찾을 수 없음"),
        },
    )
    def get(self, request: Any, class_id: int, *args: Any, **kwargs: Any) -> Response:
        class_instance = get_object_or_404(Class, id=class_id)

        page = int(request.GET.get("page", "1"))
        size = int(request.GET.get("size", "15"))
        offset = (page - 1) * size

        if page < 1:
            return Response("Page input error", status=status.HTTP_400_BAD_REQUEST)

        reviews = Review.objects.filter(class_id=class_instance.id)
        total_count = reviews.count()
        total_pages = (total_count // size) + (1 if total_count % size > 0 else 0)

        reviews = reviews.order_by("-id")[offset : offset + size]

        if not reviews.exists():
            return Response(
                {"message": "No reviews found for this class."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review_data = []
        for review in reviews:
            reactions = Reaction.get_review_reactions(review)
            review_data.append(
                {
                    "review": {
                        **ReviewSerializer(review).data,
                        "likes_count": reactions["likes_count"],
                    }
                }
            )

        response_data = {
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "reviews": review_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        methods=["POST"],
        summary="리뷰 생성",
        description="특정 클래스에 대해 새 리뷰를 생성하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id",
                description="클래스 ID",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
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
    def post(self, request: Any, class_id: int, *args: Any, **kwargs: Any) -> Response:
        try:
            class_instance = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response(
                {"class_id": "Invalid class ID."}, status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data["user"] = request.user.id
        data["class_id"] = class_instance.id

        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user, class_id=class_id)
            return Response(
                {"message": "Review successfully created.", "review": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "Review creation failed due to validation errors.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ReviewUpdateView(APIView):
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
    def patch(
        self, request: Request, class_id: int, review_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        review = get_object_or_404(Review, id=review_id, class_id=class_id)

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Review successfully updated.", "review": serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        methods=["DELETE"],
        summary="리뷰 삭제",
        description="특정 리뷰를 삭제하는 API입니다.",
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
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            204: OpenApiResponse(description="리뷰 삭제 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="리뷰를 찾을 수 없음"),
        },
    )
    def delete(
        self, request: Request, class_id: int, review_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        review = get_object_or_404(Review, id=review_id, class_id=class_id)
        review.delete()

        return Response(
            {"message": "Review successfully deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )


class ReviewImageListView(generics.ListAPIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

    serializer_class = ReviewImageSerializer

    @extend_schema(
        methods=["GET"],
        summary="특정 리뷰의 이미지 목록 조회",
        description="특정 리뷰에 연결된 이미지 목록을 페이지네이션 형태로 조회하는 API입니다.",
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
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="page",
                description="페이지 번호",
                required=False,
                default=1,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="size",
                description="페이지당 항목 수",
                required=False,
                default=15,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="리뷰 이미지 목록 조회 성공",
                response=inline_serializer(
                    name="PhotoReviewListResponse",
                    fields={
                        "total_count": serializers.IntegerField(),
                        "total_pages": serializers.IntegerField(),
                        "current_page": serializers.IntegerField(),
                        "images": serializers.ListSerializer(
                            child=inline_serializer(
                                name="PhotoReviewImageData",
                                fields={
                                    "id": serializers.IntegerField(),
                                    "image_url": serializers.CharField(),
                                },
                            )
                        ),
                    },
                ),
            ),
            404: OpenApiResponse(description="이미지를 찾을 수 없음"),
        },
    )
    def get(
        self, request: Request, class_id: int, review_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        page = int(request.GET.get("page", "1"))
        size = int(request.GET.get("size", "10"))
        offset = (page - 1) * size

        if page < 1:
            return Response("Page input error", status=status.HTTP_400_BAD_REQUEST)

        review_images = ReviewImage.objects.filter(
            review_id=review_id, review__class_id=class_id
        )
        total_count = review_images.count()
        total_pages = (total_count // size) + (1 if total_count % size > 0 else 0)

        review_images = review_images.order_by("-id")[offset : offset + size]

        if not review_images.exists():
            return Response(
                {"message": "No images found for this review."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReviewImageSerializer(review_images, many=True)
        response_data = {
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "images": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class PhotoReviewListView(generics.ListAPIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

    serializer_class = ReviewImageSerializer

    @extend_schema(
        methods=["GET"],
        summary="특정 클래스의 리뷰 이미지 목록 조회",
        description="특정 클래스에 연결된 리뷰 이미지 목록을 조회하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id",
                description="클래스 ID",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="특정 클래스 리뷰 이미지 목록 조회 성공",
                response=inline_serializer(
                    name="PhotoReviewListResponse",
                    fields={
                        "images": serializers.ListSerializer(
                            child=inline_serializer(
                                name="PhotoReviewImageData",
                                fields={
                                    "id": serializers.IntegerField(),
                                    "image_url": serializers.CharField(),
                                },
                            )
                        )
                    },
                ),
            ),
            404: OpenApiResponse(description="이미지를 찾을 수 없음"),
        },
    )
    def get(
        self, request: Request, class_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        review_images = ReviewImage.objects.filter(review__class_id=class_id)

        if not review_images.exists():
            return Response(
                {"message": "No images found for this class."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReviewImageSerializer(review_images, many=True)
        return Response({"images": serializer.data}, status=status.HTTP_200_OK)
