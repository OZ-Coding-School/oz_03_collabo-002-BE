from typing import Any

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from config.logger import logger
from users.services.token_service import Token, set_cookies


class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(
        methods=["POST"],
        summary="토큰 재발급",
        description="refresh_token을 이용한 access_token 재발급 API입니다.",
        request=None,
        parameters=[
            OpenApiParameter(
                name="refresh_token",
                type=str,
                location=OpenApiParameter.COOKIE,
                description="Refresh token from cookies",
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiTypes.OBJECT,
            status.HTTP_400_BAD_REQUEST: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Token is valid",
                summary="토큰 재발급 성공",
                value={
                    "detail": "success",
                },
                status_codes=[status.HTTP_200_OK],
            ),
            OpenApiExample(
                "Invalid Token",
                summary="유효하지 않은 리프레시 토큰",
                value={
                    "detail": "Invalid refresh token.",
                },
                status_codes=[status.HTTP_400_BAD_REQUEST],
            ),
        ],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info("refresh_token 재발급 request")
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found in cookies."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            request.data["refresh"] = refresh_token
            response = super().post(request)

            if response.status_code == 200:
                new_refresh_token = response.data.get("refresh")
                new_access_token = response.data.get("access")
                tokens = Token(new_refresh_token, new_access_token)

                response = set_cookies(request, response, tokens)

            del response.data["access"]
            del response.data["refresh"]

            return response
        except InvalidToken:
            logger.info("Invalid refresh")
            return Response(
                {"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST
            )


class CustomTokenVerifyView(TokenVerifyView):
    @extend_schema(
        methods=["POST"],
        summary="토큰 검증",
        description="access_token 검증 API입니다.",
        request=None,
        parameters=[
            OpenApiParameter(
                name="access_token",
                type=str,
                location=OpenApiParameter.COOKIE,
                description="Access token from cookies",
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiTypes.OBJECT,
            status.HTTP_401_UNAUTHORIZED: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Valid Token",
                summary="Token is valid",
                description="This response indicates that the provided token is valid.",
                value={
                    "detail": "Token is valid",
                },
                status_codes=[status.HTTP_200_OK],
            ),
            OpenApiExample(
                "Invalid Token",
                summary="Token is invalid or expired",
                description="This response indicates that the provided token is invalid or has expired.",
                value={
                    "detail": "Token is invalid or expired",
                },
                status_codes=[status.HTTP_401_UNAUTHORIZED],
            ),
        ],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info("access_token verify request")
        access_token = request.COOKIES.get("access_token")

        if access_token is None:
            return Response(
                {"detail": "Access token not found in cookies."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["token"] = access_token

        try:
            super().post(request)
            return Response({"detail": "Token is valid"}, status=status.HTTP_200_OK)

        except InvalidToken:
            logger.info("access_token invalid")
            return Response(
                {"detail": "Token is invalid or expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
