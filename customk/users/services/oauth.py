from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from config.logger import logger
from users.models import User

from .token_service import generate_tokens, set_cookies


def auth_return_response(service: str, **user_info) -> Response:
    user, created = User.objects.get_or_create(
        email=user_info["email"],
        defaults={
            "name": user_info["name"],
            "profile_image": user_info["profile_image"],
        },
    )

    if created:
        response = Response(
            {"redirect_url": "https://naver.com"}, status=status.HTTP_201_CREATED
        )
        user.set_unusable_password()
        user.save()
    else:
        user.last_login = timezone.now()
        response = Response(
            {"redirect_url": "https://google.com"}, status=status.HTTP_200_OK
        )

    logger.info(f"{service} created user, {created}")
    tokens = generate_tokens(user)
    set_cookies(response, tokens)

    return response
