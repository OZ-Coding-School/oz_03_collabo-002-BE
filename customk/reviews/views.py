from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews.models import Review
from reviews.serializers import ReviewSerializer
from classes.models import Class

from reactions.models import Reaction


class ReviewListView(APIView):
    def get(self, request, class_id, *args, **kwargs):
        class_id = Class.objects.get(id=class_id)

        reviews = Review.objects.filter(class_id=class_id)

        if not reviews.exists():
            return Response({"message": "No reviews found for this class."}, status=404)

        review_data = []
        for review in reviews:
            reactions = Reaction.get_review_reactions(review)
            review_data.append(
                {
                    "review": ReviewSerializer(review).data,
                    "likes_count": reactions["likes_count"],
                    "dislikes_count": reactions["dislikes_count"],
                }
            )

        response_data = {
            "reviews": review_data,
        }
        return Response(response_data, status=200)

    def post(self, request, class_id, *args, **kwargs):
        try:
            class_id = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return Response({"class_id": "Invalid class ID."}, status=400)

        data = request.data.copy()
        data["user"] = request.user.id
        data["class_id"] = class_id.id

        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user, class_id=class_id)
            return Response(
                {"message": "Review successfully created.", "review": serializer.data},
                status=201,
            )

        return Response(serializer.errors, status=400)

    def patch(self, request, class_id, *args, **kwargs):
        review_id = request.data.get("id")

        if not review_id:
            return Response({"error": "Review ID is required for update."}, status=400)

        review = get_object_or_404(Review, id=review_id, class_id=class_id)

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Review successfully updated.", "review": serializer.data},
                status=200,
            )

        return Response(serializer.errors, status=400)

    def delete(self, request, class_id, review_id, *args, **kwargs):
        review = get_object_or_404(Review, id=review_id, class_id=class_id)
        review.delete()

        return Response({"message": "Review successfully deleted."}, status=204)
