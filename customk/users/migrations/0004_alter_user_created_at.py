# Generated by Django 5.1 on 2024-08-21 13:30

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_rename_nickname_user_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]