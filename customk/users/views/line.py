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


@create_social_login_schema("Line")
@api_view(["POST"])
@permission_classes([AllowAny])
def callback(request: Request) -> Response:
    logger.info("line callback request")

    code = request.data.get("code")
    client_id = request.data.get("client_id")
    secret_id = os.environ.get("LINE_SECRET_ID")
    redirect_uri = os.environ.get("LINE_REDIRECT_URI")

    if not code:
        return Response(
            {"error": "Authorization code not provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token_url = "https://api.line.me/oauth2/v2.1/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": secret_id,
        }

        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code != 200:
            return Response(
                {"error": "Failed to obtain access token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tokens = response.json()

        id_token = tokens.get("id_token")

        data = {"id_token": id_token, "client_id": client_id}

        line_url = "https://api.line.me/oauth2/v2.1/verify"

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        profile_response = requests.post(line_url, headers=headers, data=data)

        if profile_response.status_code != 200:
            return Response(
                {"error": "Failed to get user profile"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile_response.raise_for_status()
        profile = profile_response.json()

        email = profile.get("email")
        name = profile.get("name")
        profile_image = profile.get("picture")

        if not profile_image:
            profile_image = "default.image.uri"  # TODO: 기본 이미지 필요

        if not email:
            logger.warning("line email empty")
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

        return auth_return_response(service="line", **user_data)

    except requests.RequestException as e:
        return Response(
            f"Error during Line authentication: {str(e)}",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except ValidationError as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
