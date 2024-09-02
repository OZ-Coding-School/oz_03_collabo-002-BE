from .models import Favorite
from django.db import transaction


@transaction.atomic
def add_favorite_class(user_id: int, class_id: int) -> Favorite:
    return Favorite.objects.create(user_id=user_id, klass=class_id)


def delete_favorite_class(user_id: int, class_id: int) -> None:
    Favorite.objects.filter(user_id=user_id, class_id=class_id).delete()