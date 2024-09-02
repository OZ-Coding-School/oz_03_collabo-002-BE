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

from classes.serializers import ClassSerializer

from .models import Favorite
from .serializers import FavoriteSerializer
from .services import add_favorite_class, delete_favorite_class


class FavoriteView(APIView):
    @extend_schema(
        methods=["GET"],
        summary="찜한 클래스 목록 조회",
        description="유저가 찜한 클래스 목록을 페이지네이션형태로 가져옵니다",
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
                name="FavoriteListResponse",
                fields={
                    "total_count": serializers.IntegerField(),
                    "total_pages": serializers.IntegerField(),
                    "current_page": serializers.IntegerField(),
                    "results": ClassSerializer(many=True),
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

        total_count = Favorite.objects.filter(user_id=user.id).count()
        total_pages = (total_count // size) + 1

        favorites = Favorite.objects.filter(user_id=user.id).order_by("-id")[
            offset : offset + size
        ]

        serializer = FavoriteSerializer(favorites, many=True)

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
        summary="찜 클래스 생성",
        description="찜 할 클래스를 생성하는 API",
        parameters=[
            OpenApiParameter(
                name="class_id",
                description="찜할 클래스 id",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            )
        ],
        request=None,
        responses={
            200: OpenApiResponse(description="이미 찜한 클래스입니다."),
            201: OpenApiResponse(
                description="클래스 생성 성공", response=ClassSerializer
            ),
            400: OpenApiResponse(description="class_id is required"),
        },
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        class_id = int(request.GET.get("class_id", 0))

        if class_id == 0:
            return Response(
                {"error": "class_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        favorite, created = add_favorite_class(
            user_id=request.user.id, class_id=class_id
        )
        serializer = FavoriteSerializer(favorite)

        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Already favorited"}, status=status.HTTP_200_OK)

    @extend_schema(
        methods=["DELETE"],
        summary="찜 한 클래스 삭제",
        description="찜 한 클래스를 삭제하는 API",
        parameters=[
            OpenApiParameter(
                name="favorite_id",
                description="삭제할 찜 id",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            )
        ],
        request=None,
        responses={
            204: OpenApiResponse(description="클래스 삭제 성공"),
            400: OpenApiResponse(description="class_id is required"),
        },
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        favorite_id = int(request.GET.get("favorite_id", 0))

        if favorite_id == 0:
            return Response(
                {"error": "class_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        delete_favorite_class(favorite_id=favorite_id)

        return Response(
            {"message": "success delete"}, status=status.HTTP_204_NO_CONTENT
        )
