from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews.models import Review
from reviews.serializers import ReviewSerializer
from classes.models import Class


class ReviewListView(APIView):
    def get(self, request, class_id, *args, **kwargs):
        try:
            course = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"class_id": "Invalid class ID."}, status=400)

        reviews = Review.objects.filter(course=course)
        if not reviews.exists():
            return Response({"message": "No reviews found for this class."}, status=404)

        serializer = ReviewSerializer(reviews, many=True)

        return Response(serializer.data, status=200)

    def post(self, request, class_id, *args, **kwargs):
        try:
            course = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"class_id": "Invalid class ID."}, status=400)

        data = request.data.copy()
        data["course"] = course.id

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, course=course)
            return Response(
                {"message": "Review successfully created.", "review": serializer.data}, status=201
            )

        return Response(serializer.errors, status=400)

    def patch(self, request, class_id, *args, **kwargs):
        review_id = request.data.get("id")

        if not review_id:
            return Response({"error": "Review ID is required for update."}, status=400)

        review = get_object_or_404(Review, id=review_id, course_id=class_id)

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Review successfully updated.", "review": serializer.data}, status=200
            )

        return Response(serializer.errors, status=400)

    def delete(self, request, class_id, review_id, *args, **kwargs):
        review = get_object_or_404(Review, id=review_id, course_id=class_id)
        review.delete()

        return Response({"message": "Review successfully deleted."}, status=204)
