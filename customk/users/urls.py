from django.urls import path

from .views import kakao
from .views.token import CustomTokenRefreshView, CustomTokenVerifyView
from .views.user import LoginView, LogoutView, SignupView, UserDetailView

urlpatterns = [
    path("kakao/callback/", kakao.callback, name="kakao_callback"),
    path("kakao/logout/", kakao.logout, name="kakao_logout"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("detail/", UserDetailView.as_view(), name="user-detail"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
]
