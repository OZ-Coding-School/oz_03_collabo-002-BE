# from django.conf import settings
from datetime import timedelta
from typing import cast

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from config import settings
from users.models import User


class Token:
    def __init__(self, refresh_token: str, access_token: str):
        self.refresh_token = refresh_token
        self.access_token = access_token


def generate_tokens(user: User) -> Token:
    refresh = RefreshToken.for_user(user)
    return Token(str(refresh), str(refresh.access_token))  # type: ignore


def set_cookies(response: Response, token: Token) -> Response:
    access_max_age = int(
        cast(timedelta, settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]).total_seconds()
    )
    refresh_max_age = int(
        cast(timedelta, settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]).total_seconds()
    )

    response.set_cookie(
        "access_token",
        token.access_token,
        max_age=access_max_age,
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        max_age=refresh_max_age,
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    return response
