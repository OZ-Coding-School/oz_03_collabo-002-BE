from django.urls import path

# from .views import kakao_views

from users.views.user_views import LoginView, LogoutView, SignupView, UserDetailView

urlpatterns = [
    # path("kakao/login/", kakao_views.login, name="kakao_login"),
    # path("kakao/callback/", kakao_views.callback, name="kakao_callback"),
    # path("kakao/logout/", kakao_views.logout, name="kakao_logout"),

    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("users/detail/", UserDetailView.as_view(), name="user-detail"),
]
