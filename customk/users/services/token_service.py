from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class Token:
    def __init__(self, refresh_token: str, access_token: str):
        self.refresh_token = refresh_token
        self.access_token = access_token


def generate_tokens(user: User) -> Token:
    refresh = RefreshToken.for_user(user)
    return Token(str(refresh), str(refresh.access_token))  # type: ignore
    # return {
    #     "access_token": str(refresh.access_token),  # type: ignore
    #     "refresh_token": str(refresh),
    # }


def set_cookies(response: Response, token: Token) -> Response:
    response.set_cookie(
        "access_token",
        token.access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    return response
