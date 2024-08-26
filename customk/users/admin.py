from django.contrib import admin, messages
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("email", "name")
