import os

import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from config.logger import logger
from users.extend_schemas.social import create_social_login_schema
from users.services.oauth import auth_return_response


@create_social_login_schema("Kakao")
@api_view(["POST"])
@permission_classes([AllowAny])
def callback(request: Request) -> Response:
    logger.info("카카오 callback request")
    code = request.data.get("code")
    client_id = os.environ.get("KAKAO_CLIENT_ID")

    if not code:
        return Response(
            "Authorization code is missing", status=status.HTTP_400_BAD_REQUEST
        )

    try:
        kakao_token_url = "https://kauth.kakao.com/oauth/token"
        kakao_profile_url = "https://kapi.kakao.com/v2/user/me"

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

        email = profile_info.get("kakao_account", {}).get("email")
        name = profile_info.get("properties", {}).get("nickname")
        profile_image = profile_info.get("properties", {}).get("profile_image")

        if not email:
            logger.warning("kakao email empty")
            return Response(
                data={
                    "message": "이메일이 존재하지 않습니다.",
                    "result": {
                        "name": name,
                        "profile_image": profile_image,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_data = {
            "email": email,
            "name": name,
            "profile_image": profile_image,
        }

        return auth_return_response(service="kakao", **user_data)

    except requests.RequestException as e:
        return Response(
            f"Error during Kakao authentication: {str(e)}",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except ValidationError as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
