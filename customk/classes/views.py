from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Class
from .serializers import ClassSerializer
from rest_framework.permissions import IsAuthenticated


class ClassListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        classes = Class.objects.all()
        serializer = ClassSerializer(classes, many=True)
        response_data = {
            "status": "success",
            "message": "Event fetched successfully",
            "data": serializer.data,
        }
        return Response(response_data, status=200)

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
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

    def patch(self, request, *args, **kwargs):
        self.check_permissions(request)
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

    def delete(self, request, *args, **kwargs):
        self.check_permissions(request)
        class_id = request.data.get("id", None)
        if class_id is None:
            return Response(
                {"status": "error", "message": "Class ID not provided"}, status=400
            )

        try:
            class_instance = Class.objects.get(id=class_id)
            class_instance.delete()
            return Response(
                {"status": "success", "message": "Event deleted successfully"},
                status=204,
            )
        except Class.DoesNotExist:
            return Response(
                {"status": "error", "message": "Event not found"}, status=404
            )

    def check_permissions(self, request):
        if not request.user.is_staff:
            self.permission_denied(request, message="관리자 권한이 필요합니다")
