# Generated by Django 5.1 on 2024-08-21 21:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reviews", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="review",
            old_name="course",
            new_name="class_id",
        ),
        migrations.RenameField(
            model_name="review",
            old_name="user",
            new_name="user_id",
        ),
    ]
