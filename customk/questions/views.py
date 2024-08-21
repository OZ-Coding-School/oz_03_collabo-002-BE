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
        questions = Question.objects.filter(class_id=class_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

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

    def delete(self, request, question_id, *args, **kwargs):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found."}, status=404)

        if question.user != request.user:
            return Response(
                {"error": "You do not have permission to delete this question."}, status=403
            )

        question.delete()
        response_data = {
            "status": "success",
            "message": "Question deleted successfully",
            "data": None,
        }
        return Response(response_data, status=200)


class AnswerListView(APIView):
    # permission_classes = [IsAuthenticated]  # 인증 및 커스텀 권한 클래스
    permission_classes = [AllowAny]

    def get(self, request, class_id, *args, **kwargs):
        answers = Answer.objects.filter(question_id__class_id=class_id)
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)

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
                {"error": "Question not found or does not belong to this class."}, status=404
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

    def delete(self, request, class_id, *args, **kwargs):
        answer_id = request.data.get("answer_id")

        if not answer_id:
            return Response({"error": "Answer ID is required."}, status=400)

        try:
            answer = Answer.objects.get(id=answer_id, question__class_id=class_id)
        except Answer.DoesNotExist:
            return Response(
                {"error": "Answer not found or does not belong to this class."}, status=404
            )

        if answer.user != request.user:
            return Response(
                {"error": "You do not have permission to delete this answer."}, status=403
            )

        answer.delete()
        return Response({"status": "success", "message": "Answer deleted successfully"}, status=200)
