from django.db import transaction

from .models import Favorite


@transaction.atomic
def add_favorite_class(user_id: int, class_id: int) -> tuple[Favorite, bool]:
    return Favorite.objects.get_or_create(user_id=user_id, class_id=class_id)


def delete_favorite_class(favorite_id: int) -> None:
    Favorite.objects.filter(id=favorite_id).delete()
