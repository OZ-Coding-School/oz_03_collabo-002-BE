from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from users.serialirizers.user_serializer import UserSerializer, UserUpdateSerializer
from users.services.token_service import generate_tokens, set_cookies


class SignupView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        methods=['POST'],
        summary='일반 회원가입',
        description='일반 회원가입 API',
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description='회원가입 실패')
        },
    )
    def post(self, request: Request) -> Response:
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = serializer.save()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            return response
        except IntegrityError as e:
            return self.handle_integrity_error(e)

    def handle_integrity_error(self, error):
        error_message = "데이터베이스 무결성 오류가 발생했습니다."
        if "unique constraint" in str(error).lower():
            error_message = "이미 사용 중인 이메일입니다. 다른 이메일을 사용해주세요."
        return Response({"error_message": error_message}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    @extend_schema(
        methods=['GET'],
        summary='유저 정보 조회',
        description='특정 유저 조회 API',
        request=UserSerializer,
        responses={
            200: UserSerializer,
            404: OpenApiResponse(description='존재하지 않는 유저')
        },
    )
    def get(self, request: Request):
        user = request.user
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @extend_schema(
        methods=['PATCH'],
        summary='유저 정보 업데이트',
        description='유저 정보 업데이트 API',
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description='잘못된 요청')
        },
    )
    def patch(self, request: Request):
        user = request.user
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


    @extend_schema(
        methods=['DELETE'],
        summary='유저 탈퇴',
        description='유저 탈퇴 API',
        request=UserSerializer,
        responses={
            204: OpenApiResponse(description='탈퇴에 성공하였습니다')
        }
    )
    def delete(self, request: Request) -> Response:
        user = request.user
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        methods=['POST'],
        summary='로그인',
        description='로그인 API',
        request=UserSerializer,
        responses={
            200: OpenApiResponse(description='로그인 성공'),
            401: OpenApiResponse(description='로그인 실패')
        }
    )
    def post(self, request: Request) -> Response:
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        tokens = generate_tokens(user)

        response = Response(data={"status": "success",
                                  "message": "로그인 성공"}, status=status.HTTP_200_OK)
        set_cookies(response, tokens)

        return response


@extend_schema(
    methods=['POST'],
    summary="로그아웃",
    description="로그아웃 API",
    request=UserSerializer,
    responses={
        200: "로그아웃 성공",
        401: OpenApiResponse(description='로그아웃 실패')
    },
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        logout(request)

        return Response(data={"message": "로그아웃 성공"}, status=status.HTTP_200_OK)
