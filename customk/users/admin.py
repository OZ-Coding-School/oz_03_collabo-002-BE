from django.contrib import admin

from users.models import User

from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type: ignore
    list_display = ("email", "name")

