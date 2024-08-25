from drf_spectacular.utils import extend_schema, OpenApiExample, inline_serializer
from rest_framework import serializers, status
from drf_spectacular.types import OpenApiTypes


def create_social_login_schema(service_name: str):
    return extend_schema(
        methods=["POST"],
        summary=f"{service_name} 로그인 callback",
        description=f"로그인 성공 시 HttpOnly 쿠키에 JWT 토큰이 전달됩니다.",
        request=inline_serializer(
            name=f"{service_name}InlineFormSerializer",
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
                value={"error": f"Error during {service_name} authentication: {{error message}}"},
                response_only=True,
                status_codes=[status.HTTP_500_INTERNAL_SERVER_ERROR],
            ),
        ],
    )