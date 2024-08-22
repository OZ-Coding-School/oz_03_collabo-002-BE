from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from common.models import CommonModel


class UserManager(BaseUserManager["User"]):
    # 일반 유저 생성 함수
    def create_user(self, email: str, password: str) -> "User":
        if not email:
            raise ValueError("이메일이 필요합니다")

        user = self.model(email=email)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email: str, password: str) -> "User":
        user = self.create_user(email, password)

        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin, CommonModel):
    email = models.EmailField(max_length=255, unique=True, editable=False)
    name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self) -> str:
        return f"name: {self.name}"
