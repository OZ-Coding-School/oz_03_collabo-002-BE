from django.urls import path

from users.views.user import LoginView, LogoutView, SignupView, UserDetailView

from .views import kakao

urlpatterns = [
    path("kakao/callback/", kakao.callback, name="kakao_callback"),
    path("kakao/logout/", kakao.logout, name="kakao_logout"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("detail/", UserDetailView.as_view(), name="user-detail"),
]
