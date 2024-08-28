from typing import Any, Dict

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Class
from .serializers import ClassSerializer


class ClassListView(APIView):
    @extend_schema(
        methods=["GET"],
        summary="클래스 목록 조회",
        description="등록된 클래스 목록을 조회하는 API입니다.",
        responses={
            200: OpenApiResponse(
                description="클래스 목록 조회 성공", response=ClassSerializer(many=True)
            ),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        classes = Class.objects.all()
        serializer = ClassSerializer(classes, many=True)
        response_data = {
            "status": "success",
            "message": "Event fetched successfully",
            "data": serializer.data,
        }
        return Response(response_data, status=200)

    @extend_schema(
        methods=["POST"],
        summary="클래스 생성",
        description="새 클래스를 생성하는 API입니다.",
        request=ClassSerializer,
        responses={
            201: OpenApiResponse(
                description="클래스 생성 성공", response=ClassSerializer
            ),
            400: OpenApiResponse(description="잘못된 요청"),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status": "success",
                "message": "Event created successfully",
                "data": serializer.data,
            }
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)

    @extend_schema(
        methods=["PATCH"],
        summary="클래스 업데이트",
        description="기존 클래스를 업데이트하는 API입니다.",
        request=ClassSerializer,
        responses={
            200: OpenApiResponse(
                description="클래스 업데이트 성공", response=ClassSerializer
            ),
            400: OpenApiResponse(description="잘못된 요청"),
        },
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status": "success",
                "message": "Event updated successfully",
                "data": serializer.data,
            }
            return Response(response_data, status=200)
        return Response(serializer.errors, status=400)

    @extend_schema(
        methods=["DELETE"],
        summary="클래스 삭제",
        description="기존 클래스를 삭제하는 API입니다.",
        request=None,
        responses={
            204: OpenApiResponse(description="클래스 삭제 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="클래스가 존재하지 않음"),
        },
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        class_id = request.data.get("id", None)
        if class_id is None:
            return Response(
                {"status": "error", "message": "Class ID not provided"}, status=400
            )

        try:
            class_instance = Class.objects.get(id=class_id)
            class_instance.delete()
            return Response(
                {"status": "success", "message": "삭제 성공했습니다"},
                status=204,
            )
        except Class.DoesNotExist:
            return Response(
                {"status": "error", "message": "삭제 실패했습니다"}, status=404
            )
