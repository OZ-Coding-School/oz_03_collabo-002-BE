import os

import requests
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from config.logger import logger
from users.services.oauth import auth_return_response


@extend_schema(
    methods=["POST"],
    summary="구글 로그인 callback",
    description="로그인 성공 시 HttpOnly 쿠키에 JWT 토큰이 전달됩니다.",
    request=inline_serializer(
        name="InlineFormSerializer",
        fields={
            "code": serializers.CharField(help_text="OAuth 인증 코드"),
            "client_id": serializers.CharField(help_text="OAuth 인증키"),
        },
    ),
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Success response",
            value={"redirect_url": "https://example.com"},
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
        OpenApiExample(
            "이메일 가져오기 실패",
            value={
                "message": "OAuth 서비스에 등록된 이메일이 존재하지 않습니다.",
                "result": {
                    "name": "name",
                    "profile_image": "profile_image",
                },
            },
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            "Body에 코드가 없는 경우",
            value={"error": "Authorization code not provided"},
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            "Access Token 발급 실패",
            value={"error": "Failed to obtain access token"},
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            "프로필 정보 가져오기 실패",
            value={"error": "Failed to get user profile"},
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            "서버 에러",
            value={"error": "Error during Google authentication: {error message}"},
            response_only=True,
            status_codes=[status.HTTP_500_INTERNAL_SERVER_ERROR],
        ),
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def callback(request: Request) -> Response:
    logger.info("구글 callback request")

    code = request.data.get("code")
    client_id = request.data.get("client_id")

    if not code:
        return Response(
            {"error": "Authorization code not provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": os.environ.get("GOOGLE_SECRET_ID"),
            "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI"),  # required
            "grant_type": "authorization_code",
        }

        response = requests.post(token_url, data=data)

        if response.status_code != 200:
            return Response(
                {"error": "Failed to obtain access token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tokens = response.json()
        access_token = tokens.get("access_token")

        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code != 200:
            return Response(
                {"error": "Failed to get user info"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        email = user_info.get("email")
        name = user_info.get("name")
        profile_image = user_info.get("picture")

        if not email:
            logger.warning("google email empty")
            return Response(
                "Email not provided by google", status=status.HTTP_400_BAD_REQUEST
            )

        user_data = {
            "email": email,
            "name": name,
            "profile_image": profile_image,
        }

        return auth_return_response(service="google", **user_data)

    except requests.RequestException as e:
        return Response(
            f"Error during Google authentication: {str(e)}",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except ValidationError as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
