from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import User


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request: Request):
        raw_token = request.COOKIES.get("access_token")

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)  # type: ignore
            return self.get_user(validated_token), validated_token

        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")


class JWTAuthenticationCookieScheme(OpenApiAuthenticationExtension):
    target_class = "config.authentication.CookieJWTAuthentication"
    name = "CookieAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": 'JWT access_token과 refresh_token은 HttpOnly 쿠키로 전달됩니다. \
                           access_token은 "access_token" 쿠키로, refresh_token은 "refresh_token" 쿠키로 전송됩니다.',
        }
