import os
from datetime import timedelta
from typing import cast

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from config import settings
from config.logger import logger
from users.models import User


class Token:
    def __init__(self, refresh_token: str, access_token: str):
        self.refresh_token = refresh_token
        self.access_token = access_token


def generate_tokens(user: User) -> Token:
    refresh = RefreshToken.for_user(user)
    return Token(str(refresh), str(refresh.access_token))  # type: ignore


def get_cookie_domain(env: str) -> str | None:
    if env == "production":
        return os.environ.get("DOMAIN_NAME")
    return None


def set_token_cookie(
    response: Response, name: str, token: str, max_age: int, front_env: str
) -> None:
    domain = get_cookie_domain(front_env)

    response.set_cookie(
        key=name,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=(front_env != "development"),
        samesite="Lax" if front_env == "development" else "None",
        domain=domain if domain else None,
    )


def set_cookies(request: Request, response: Response, token: Token) -> Response:
    host = request.get_host()
    logger.info(f"Setting cookies domain: {host}")

    if host and str(os.getenv("DOMAIN_NAME")) in host:
        front_env = "production"
    else:
        front_env = "development"

    access_max_age = int(
        cast(timedelta, settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]).total_seconds()
    )
    refresh_max_age = int(
        cast(timedelta, settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]).total_seconds()
    )

    set_token_cookie(
        response, "access_token", token.access_token, access_max_age, front_env
    )
    set_token_cookie(
        response, "refresh_token", token.refresh_token, refresh_max_age, front_env
    )

    return response
