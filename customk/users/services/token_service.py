from datetime import timedelta
from typing import cast
from urllib.parse import urlparse

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


def get_domain(request: Request) -> str:
    origin = request.headers.get("Origin")
    if not origin:
        return ""

    try:
        parsed_url = urlparse(origin)
        return parsed_url.hostname or ""
    except ValueError:
        return ""


def set_cookies(request: Request, response: Response, token: Token) -> Response:
    domain = get_domain(request)
    logger.info(f"Set cookie - Domain: {domain}")

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
        secure=True,
        httponly=True,
        samesite="None",
        domain=domain,
    )

    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        max_age=refresh_max_age,
        secure=True,
        httponly=True,
        samesite="None",
        domain=domain,
    )

    if hasattr(response, 'data'):
        response.data['access_token'] = token.access_token
        response.data['refresh_token'] = token.refresh_token
    else:
        response.data = {'access_token': token.access_token, 'refresh_token': token.refresh_token}

    return response
