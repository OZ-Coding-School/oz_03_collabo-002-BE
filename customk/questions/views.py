from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
from classes.models import Class


class QuestionListView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get(self, request, class_id, *args, **kwargs):
        # 특정 수업에 대한 질문들만 가져오기
        questions = Question.objects.filter(course_id=class_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request, class_id, *args, **kwargs):
        try:
            course = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"error": "Class not found."}, status=404)

        # 요청 데이터 복사 및 사용자와 수업 정보 추가
        data = request.data.copy()
        data["user"] = request.user.id
        data["course"] = course.id

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

    def delete(self, request, question_id, *args, **kwargs):
        question = Question.objects.filter(id=question_id)
        question.delete()
        response_data = {
            "status": "success",
            "message": "Question deleted successfully",
            "data": None
        }
        return Response(response_data, status=201)


class AnswerListView(APIView):
    # permission_classes = [IsAuthenticated]  # 인증 및 커스텀 권한 클래스
    permission_classes = [AllowAny]

    def get(self, request, class_id, *args, **kwargs):
        answers = Answer.objects.filter(question__course_id=class_id)
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)

    def post(self, request, class_id, *args, **kwargs):
        try:
            Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"error": "Class not found."}, status=404)

        question_id = request.data.get("question")
        try:
            question = Question.objects.get(id=question_id, course_id=class_id)
        except Question.DoesNotExist:
            return Response(
                {"error": "Question not found or does not belong to this class."}, status=404
            )

        data = request.data.copy()
        data["user"] = request.user.id
        data["question"] = question.id

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
