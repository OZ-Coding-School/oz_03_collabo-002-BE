from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Class, ClassDate, ClassImages
from .serializers import ClassSerializer, ClassDateSerializer, ClassImagesSerializer


class ClassListView(APIView):
    def get(self, request, *args, **kwargs):
        classes = Class.objects.all()
        serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request, *args, **kwargs):
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

    def delete(self, request, *args, **kwargs):
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=204)
