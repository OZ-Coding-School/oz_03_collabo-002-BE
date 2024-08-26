from typing import Any

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from classes.models import Class
from questions.models import Answer, Question
from questions.serializers import AnswerSerializer, QuestionSerializer


class QuestionListView(APIView):
    @extend_schema(
        methods=["GET"],
        summary="질문 목록 조회",
        description="특정 클래스에 대한 질문 목록을 조회하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id", description="클래스 ID", required=True, type=int
            )
        ],
        responses={
            200: OpenApiResponse(
                description="질문 목록 조회 성공",
                response=inline_serializer(
                    name="QuestionListResponse",
                    fields={
                        "questions": serializers.ListSerializer(
                            child=QuestionSerializer()
                        )
                    },
                ),
            ),
            404: OpenApiResponse(description="클래스를 찾을 수 없음"),
        },
    )
    def get(
        self, request: Request, class_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        questions = Question.objects.filter(class_id=class_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    @extend_schema(
        methods=["POST"],
        summary="질문 생성",
        description="특정 클래스에 대해 새 질문을 생성하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id", description="클래스 ID", required=True, type=int
            )
        ],
        request=QuestionSerializer,
        responses={
            201: OpenApiResponse(
                description="질문 생성 성공",
                response=inline_serializer(
                    name="QuestionCreateResponse",
                    fields={
                        "status": serializers.CharField(),
                        "message": serializers.CharField(),
                        "data": QuestionSerializer(),
                    },
                ),
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="클래스를 찾을 수 없음"),
        },
    )
    def post(
        self, request: Request, class_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        try:
            class_instance = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"error": "Class not found."}, status=404)

        # 요청 데이터 복사 및 사용자와 수업 정보 추가
        data = request.data.copy()
        data["user_id"] = request.user.id
        data["class_id"] = class_instance.id

        serializer = QuestionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status": "success",
                "message": "Question submitted successfully",
                "data": serializer.data,
            }
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)

    @extend_schema(
        methods=["PATCH"],
        summary="질문 업데이트",
        description="특정 질문을 업데이트하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id", description="클래스 ID", required=True, type=int
            ),
        ],
        request=QuestionSerializer,
        responses={
            200: OpenApiResponse(
                description="질문 업데이트 성공",
                response=inline_serializer(
                    name="QuestionUpdateResponse",
                    fields={
                        "status": serializers.CharField(),
                        "message": serializers.CharField(),
                        "data": QuestionSerializer(),
                    },
                ),
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="질문을 찾을 수 없음"),
            403: OpenApiResponse(description="권한 없음"),
        },
    )
    def patch(
        self, request: Request, class_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        question_id = request.data.get("id")
        if question_id is None:
            return Response({"error": "Question ID is required."}, status=400)

        try:
            question = Question.objects.get(id=int(question_id), class_id=class_id)
        except Question.DoesNotExist:
            return Response(
                {"error": "Question not found or does not belong to this class."},
                status=404,
            )

        if question.user_id != request.user:
            return Response(
                {"error": "You do not have permission to update this question."},
                status=403,
            )

        serializer = QuestionSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Question updated successfully",
                    "data": serializer.data,
                },
                status=200,
            )

        return Response(serializer.errors, status=400)

    @extend_schema(
        methods=["DELETE"],
        summary="질문 삭제",
        description="특정 질문을 삭제하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="question_id", description="질문 ID", required=True, type=int
            )
        ],
        responses={
            200: OpenApiResponse(
                description="질문 삭제 성공",
                response=inline_serializer(
                    name="QuestionDeleteResponse",
                    fields={
                        "status": serializers.CharField(),
                        "message": serializers.CharField(),
                        "data": AnswerSerializer(),
                    },
                ),
            ),
            404: OpenApiResponse(description="질문을 찾을 수 없음"),
            403: OpenApiResponse(description="권한 없음"),
        },
    )
    def delete(
        self, request: Request, question_id: int, *args: Any, **kwargs: Any
    ) -> Response:
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found."}, status=404)

        if question.user_id != request.user.id:
            return Response(
                {"error": "You do not have permission to delete this question."},
                status=403,
            )

        question.delete()
        response_data = {
            "status": "success",
            "message": "Question deleted successfully",
            "data": None,
        }
        return Response(response_data, status=200)
