from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import response


def generate_tokens(user) -> dict:
    refresh = RefreshToken.for_user(user)

    return {
        "access_token": str(refresh.access_token),  # type: ignore
        "refresh_token": str(refresh),
    }


def set_cookies(response: response, tokens) -> response:
    response.set_cookie(
        "access_token",
        tokens["access_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    response.set_cookie(
        "refresh_token",
        tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    return response