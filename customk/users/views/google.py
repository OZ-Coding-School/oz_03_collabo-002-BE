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


@create_social_login_schema("Google")
@api_view(["POST"])
@permission_classes([AllowAny])
def callback(request: Request) -> Response:
    logger.info("구글 callback request")

    code = request.data.get("code")

    if not code:
        return Response(
            {"error": "Authorization code not provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
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

        return auth_return_response(service="google", request=request, **user_data)

    except requests.RequestException as e:
        return Response(
            f"Error during Google authentication: {str(e)}",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except ValidationError as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
