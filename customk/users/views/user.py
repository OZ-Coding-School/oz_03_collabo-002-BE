from django.db import IntegrityError
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from common.services.ncp_api_conf import ObjectStorage
from config.logger import logger
from users.serializers.user_serializer import (
    UserInfoSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from users.services.token_service import generate_tokens, set_cookies


class SignupView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        methods=["POST"],
        summary="일반 회원가입",
        description="이메일, 이름, 비밀번호, 이미지링크(optional)을 사용한 회원가입입니다",
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="회원가입 실패"),
        },
    )
    def post(self, request: Request) -> Response:
        logger.info("회원가입 request")
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            return response
        except IntegrityError as e:
            return self.handle_integrity_error(e)

    def handle_integrity_error(self, error: IntegrityError) -> Response:
        error_message = "데이터베이스 무결성 오류가 발생했습니다."
        if "unique constraint" in str(error).lower():
            error_message = "이미 사용 중인 이메일입니다. 다른 이메일을 사용해주세요."
        return Response(
            {"error_message": error_message}, status=status.HTTP_400_BAD_REQUEST
        )


class UserDetailView(APIView):
    @extend_schema(
        methods=["GET"],
        summary="유저 정보 조회",
        description="이메일, 이름, 이미지가 반환됩니다",
        responses={
            200: UserInfoSerializer,
            404: OpenApiResponse(description="존재하지 않는 유저"),
        },
    )
    def get(self, request: Request) -> Response:
        logger.info("유저 조회 request")
        user = request.user
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserInfoSerializer(user)
        return Response(serializer.data)

    @extend_schema(
        methods=["PATCH"],
        summary="유저 정보 업데이트",
        description="이름 또는 이미지를 수정합니다",
        request=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer,
            400: OpenApiResponse(description="잘못된 요청"),
        },
    )
    def patch(self, request: Request) -> Response:
        logger.info("유저 업데이트 request")
        user = request.user
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        methods=["DELETE"],
        summary="유저 탈퇴",
        description="쿠키에 저장된 토큰 및 프로필 이미지도 같이 삭제됩니다",
        responses={204: OpenApiResponse(description="탈퇴에 성공하였습니다")},
    )
    def delete(self, request: Request) -> Response:
        logger.info("유저 삭제 request")
        user = request.user

        from users.models import User

        if not isinstance(user, User):
            return Response(status=status.HTTP_404_NOT_FOUND)

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            token = RefreshToken(refresh_token)  # type: ignore
            token.blacklist()

        obj = ObjectStorage()
        if user.profile_image:
            obj_status_code = obj.delete_object(user.profile_image)

            if obj_status_code != 204:
                return Response(
                    {"message": "delete image error"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user.delete()

        response = Response(
            {"message": "success delete user"}, status=status.HTTP_204_NO_CONTENT
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        methods=["POST"],
        summary="일반 로그인",
        description="로그인 성공 시 HttpOnly 쿠키에 JWT 토큰이 전달됩니다.",
        request=inline_serializer(
            name="UserLoginRequest",
            fields={
                "email": serializers.EmailField(help_text="User's email address"),
                "password": serializers.CharField(help_text="User's password"),
            },
        ),
        responses={
            200: inline_serializer(
                name="UserLoginResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "name": serializers.CharField(),
                    "email": serializers.EmailField(),
                    "profile_image": serializers.URLField(),
                },
            ),
            400: OpenApiResponse(description="Invalid credentials"),
            401: OpenApiResponse(description="Unauthorized or inactive user"),
        },
        examples=[
            OpenApiExample(
                "Successful Login",
                value={
                    "id": 1,
                    "name": "John Doe",
                    "email": "johndoe@example.com",
                    "profile_image": "https://example.com/profile_image.png",
                },
                response_only=True,
                status_codes=[200],
            ),
            OpenApiExample(
                "Invalid Credentials",
                value={"detail": "Invalid login credentials"},
                response_only=True,
                status_codes=[400],
            ),
            OpenApiExample(
                "Inactive User",
                value={"detail": "User account is deactivated"},
                response_only=True,
                status_codes=[401],
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        logger.info("Login attempt", extra={"email": request.data.get("email")})

        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        user_info_serializer = UserInfoSerializer(user)
        user_data = user_info_serializer.data

        response = Response(user_data, status=status.HTTP_200_OK)
        tokens = generate_tokens(user)
        set_cookies(request, response, tokens)

        return response


@extend_schema(
    methods=["POST"],
    summary="로그아웃",
    description="로그아웃 API",
    request=None,
    responses={
        200: OpenApiResponse(description="로그아웃 성공"),
        401: OpenApiResponse(description="로그아웃 실패"),
    },
)
class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        logger.info("로그아웃 request")
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            token = RefreshToken(refresh_token)  # type: ignore
            token.blacklist()

        response = Response(
            data={"message": "로그아웃 성공"}, status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
