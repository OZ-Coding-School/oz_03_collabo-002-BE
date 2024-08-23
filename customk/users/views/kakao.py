import os

import requests
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from config.logger import logger
from users.models import User
from users.services.token_service import generate_tokens, set_cookies


@extend_schema(
    methods=["POST"],
    summary="카카오 로그인 callback",
    description="로그인 성공 시 HttpOnly 쿠키에 JWT 토큰이 전달됩니다.",
    request=inline_serializer(
        name="InlineFormSerializer",
        fields={
            "code": serializers.CharField(help_text="OAuth 인증 코드"),
        },
    ),
    responses={
        200: OpenApiResponse(
            description="로그인 성공",
            examples=[
                OpenApiExample(
                    "Success response",
                    value={"redirect_url": "https://example.com"},
                )
            ],
        ),
        400: OpenApiResponse(description="잘못된 요청"),
        401: OpenApiResponse(description="인증 실패"),
        500: OpenApiResponse(description="서버 오류"),
    },
)
@api_view(["POST"])
def callback(request: Request) -> Response:
    logger.info("카카오 콜백 request")
    code = request.data.get("code")
    if not code:
        return Response(
            "Authorization code is missing", status=status.HTTP_400_BAD_REQUEST
        )

    try:
        kakao_token_url = os.environ.get("KAKAO_TOKEN_URL", "token_url")
        kakao_profile_url = os.environ.get("KAKAO_PROFILE_URL", "profile_url")
        client_id = os.environ.get("KAKAO_CLIENT_ID", "client_id")

        token_response = requests.post(
            kakao_token_url,
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "code": code,
            },
            timeout=30,
        )

        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        profile_response = requests.get(
            kakao_profile_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            },
            timeout=30,
        )

        profile_response.raise_for_status()
        profile_info = profile_response.json()

        kakao_email = profile_info.get("kakao_account", {}).get("email")
        kakao_username = profile_info.get("properties", {}).get("nickname")

        if not kakao_email:
            logger.warning("kakao email empty")
            return Response(
                "Email not provided by Kakao", status=status.HTTP_400_BAD_REQUEST
            )

        user, created = User.objects.get_or_create(
            email=kakao_email, defaults={"name": kakao_username}
        )

        if created:
            response = Response(
                {"redirect_url": "https://naver.com"}, status=status.HTTP_201_CREATED
            )
            user.set_unusable_password()
            user.save()
        else:
            response = Response(
                {"redirect_url": "https://google.com"}, status=status.HTTP_200_OK
            )
        logger.info(f"created user, {created}")
        tokens = generate_tokens(user)
        set_cookies(response, tokens)

        return response

    except requests.RequestException as e:
        return Response(
            f"Error during Kakao authentication: {str(e)}",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except ValidationError as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=["POST"],
    summary="카카오 로그아웃",
    description="로그아웃을 성공하면 쿠키에 jwt 토큰을 삭제합니다.",
    request=None,
    parameters=[
        OpenApiParameter(
            name="kakao_client_id",
            type=str,
            location=OpenApiParameter.HEADER,
            description="Kakao client ID",
        ),
        OpenApiParameter(
            name="refresh_token",
            type=str,
            location=OpenApiParameter.COOKIE,
            description="Refresh token from cookies",
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="로그인 성공",
            examples=[
                OpenApiExample(
                    "Success response",
                    value={"redirect_url": "https://example.com"},
                )
            ],
        ),
        401: OpenApiResponse(description="로그아웃 실패"),
    },
)
@api_view(["POST"])
def logout(request: Request) -> Response:
    logger.info("카카오 로그아웃 request")
    try:
        refresh_token = request.COOKIES.get("refresh_token")
        client_id = request.headers.get("KAKAO_CLIENT_ID")
        if not refresh_token or not client_id:
            logger.warning("토큰, client id error")
            return Response(
                "Token or Client_id not found", status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)  # type: ignore
        token.blacklist()

        kakao_logout_url = f"https://kauth.kakao.com/oauth/logout?client_id={client_id}&logout_redirect_uri=https://google.com"

        response = Response(
            {"kakao_logout_url": kakao_logout_url}, status=status.HTTP_200_OK
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response

    except Exception as e:
        return Response(
            f"Error during logout: {str(e)}",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
