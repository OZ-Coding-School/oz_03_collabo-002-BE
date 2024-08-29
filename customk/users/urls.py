from django.urls import re_path

from .views import google, kakao, line
from .views.token import CustomTokenRefreshView, CustomTokenVerifyView
from .views.user import LoginView, LogoutView, SignupView, UserDetailView

urlpatterns = [
    re_path(r"^signup/?$", SignupView.as_view(), name="signup"),
    re_path(r"^login/?$", LoginView.as_view(), name="login"),
    re_path(r"^logout/?$", LogoutView.as_view(), name="logout"),
    re_path(r"^detail/?$", UserDetailView.as_view(), name="user-detail"),
    re_path(
        r"^token/refresh/?$", CustomTokenRefreshView.as_view(), name="token_refresh"
    ),
    re_path(r"^token/verify/?$", CustomTokenVerifyView.as_view(), name="token_verify"),
    re_path(r"^kakao/callback/?$", kakao.callback, name="kakao_callback"),
    re_path(r"^google/callback/?$", google.callback, name="google_callback"),
    re_path(r"^line/callback/?$", line.callback, name="line_callback"),
]
