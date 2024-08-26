# Generated by Django 5.1 on 2024-08-20 21:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("classes", "0003_classdate_person"),
    ]

    operations = [
        migrations.AddField(
            model_name="class",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="class",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]