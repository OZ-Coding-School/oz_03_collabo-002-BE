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

from .models import Answer, Question
from .serializers import AnswerSerializer, QuestionSerializer


class QuestionListView(APIView):
    permission_classes = [IsAuthenticated]

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
    def get(self, request, class_id, *args, **kwargs):
        # 특정 수업에 대한 질문들만 가져오기
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
    def post(self, request, class_id, *args, **kwargs):
        try:
            class_id = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"error": "Class not found."}, status=404)

        # 요청 데이터 복사 및 사용자와 수업 정보 추가
        data = request.data.copy()
        data["user_id"] = request.user.id
        data["class_id"] = class_id.id

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
    def patch(self, request, class_id, *args, **kwargs):
        question_id = request.data.get("id")

        try:
            question = Question.objects.get(id=question_id, class_id=class_id)
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
    def delete(self, request, question_id, *args, **kwargs):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found."}, status=404)

        if question.user != request.user:
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


class AnswerListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        summary="답변 목록 조회",
        description="특정 클래스에 대한 모든 답변 목록을 조회하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id", description="클래스 ID", required=True, type=int
            )
        ],
        responses={
            200: OpenApiResponse(
                description="답변 목록 조회 성공",
                response=inline_serializer(
                    name="AnswerListResponse",
                    fields={
                        "answers": serializers.ListSerializer(child=AnswerSerializer())
                    },
                ),
            ),
            404: OpenApiResponse(description="클래스를 찾을 수 없음"),
        },
    )
    def get(self, request, class_id, *args, **kwargs):
        answers = Answer.objects.filter(question_id__class_id=class_id)
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)

    @extend_schema(
        methods=["POST"],
        summary="답변 생성",
        description="특정 클래스와 질문에 대해 새 답변을 생성하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id", description="클래스 ID", required=True, type=int
            )
        ],
        request=AnswerSerializer,
        responses={
            201: OpenApiResponse(
                description="답변 생성 성공",
                response=inline_serializer(
                    name="AnswerCreateResponse",
                    fields={
                        "status": serializers.CharField(),
                        "message": serializers.CharField(),
                        "data": AnswerSerializer(),
                    },
                ),
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="클래스 또는 질문을 찾을 수 없음"),
        },
    )
    def post(self, request, class_id, *args, **kwargs):
        try:
            Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"error": "Class not found."}, status=404)

        question_id = request.data.get("question_id")
        try:
            question = Question.objects.get(id=question_id, class_id=class_id)
        except Question.DoesNotExist:
            return Response(
                {"error": "Question not found or does not belong to this class."},
                status=404,
            )

        data = request.data.copy()
        data["question_id"] = question.id
        data["user_id"] = request.user.id

        serializer = AnswerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status": "success",
                "message": "Answer submitted successfully",
                "data": serializer.data,
            }
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)

    @extend_schema(
        methods=["PATCH"],
        summary="답변 업데이트",
        description="특정 답변을 업데이트하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id", description="클래스 ID", required=True, type=int
            ),
            OpenApiParameter(
                name="answer_id", description="답변 ID", required=True, type=int
            ),
        ],
        request=AnswerSerializer,
        responses={
            200: OpenApiResponse(
                description="답변 업데이트 성공",
                response=inline_serializer(
                    name="AnswerUpdateResponse",
                    fields={
                        "status": serializers.CharField(),
                        "message": serializers.CharField(),
                        "data": AnswerSerializer(),
                    },
                ),
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="답변을 찾을 수 없음"),
            403: OpenApiResponse(description="권한 없음"),
        },
    )
    def patch(self, request, class_id, *args, **kwargs):
        answer_id = request.data.get("answer_id")

        try:
            answer = Answer.objects.get(id=answer_id, question__class_id=class_id)
        except Answer.DoesNotExist:
            return Response(
                {"error": "Answer not found or does not belong to this class."},
                status=404,
            )

        if answer.user_id != request.user:
            return Response(
                {"error": "You do not have permission to update this answer."},
                status=403,
            )

        serializer = AnswerSerializer(answer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Answer updated successfully",
                    "data": serializer.data,
                },
                status=200,
            )

        return Response(serializer.errors, status=400)

    @extend_schema(
        methods=["DELETE"],
        summary="답변 삭제",
        description="특정 답변을 삭제하는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="class_id", description="클래스 ID", required=True, type=int
            ),
            OpenApiParameter(
                name="answer_id", description="답변 ID", required=True, type=int
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="답변 삭제 성공",
                response=inline_serializer(
                    name="AnswerDeleteResponse",
                    fields={
                        "status": serializers.CharField(),
                        "message": serializers.CharField(),
                        "data": None,
                    },
                ),
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="답변을 찾을 수 없음"),
            403: OpenApiResponse(description="권한 없음"),
        },
    )
    def delete(self, request, class_id, *args, **kwargs):
        answer_id = request.data.get("answer_id")

        if not answer_id:
            return Response({"error": "Answer ID is required."}, status=400)

        try:
            answer = Answer.objects.get(id=answer_id, question__class_id=class_id)
        except Answer.DoesNotExist:
            return Response(
                {"error": "Answer not found or does not belong to this class."},
                status=404,
            )

        if answer.user != request.user:
            return Response(
                {"error": "You do not have permission to delete this answer."},
                status=403,
            )

        answer.delete()
        return Response(
            {"status": "success", "message": "Answer deleted successfully"}, status=200
        )
