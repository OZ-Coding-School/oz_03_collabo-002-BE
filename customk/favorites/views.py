from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Favorite
from .serializers import FavoriteSerializer
from classes.models import Class


class FavoriteView(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        page = int(request.GET.get("page", "1"))
        size = int(request.GET.get("size", "10"))
        offset = (page - 1) * size

        if page < 1:
            return Response("page input error", status=status.HTTP_400_BAD_REQUEST)
        favorites = Favorite.objects.filter(user=request.user).order_by("-id")[offset: offset + size]

        class_ids = [favorite.class_id for favorite in favorites]
        classes = Class.objects.filter(id__in=class_ids)

        serializer = FavoriteSerializer(classes, many=True)

        total_count = len(favorites)
        total_pages = (total_count // size) + 1

        # serializer = FavoriteSerializer(favorites, many=True)

        return Response(
            {"total_count": total_count, "total_pages": total_pages, "current_page": page, "results": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        class_id = request.GET.get("class_id", "")

        if not class_id:
            return Response({"error": "klass_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        favorite, created = Favorite.objects.get_or_create(user=request.user, klass_id=class_id)
        serializer = FavoriteSerializer(favorite)

        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Already favorited"}, status=status.HTTP_200_OK)


class FavoriteDeleteView(APIView):
    def delete(self, request: Request, *args, **kwargs) -> Response:
        class_id = request.GET.get("class_id", "")
        user_id = request.user.id
        Favorite.objects.filter(user_id=user_id, id=class_id).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)