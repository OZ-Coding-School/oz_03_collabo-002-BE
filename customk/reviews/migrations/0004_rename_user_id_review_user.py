# Generated by Django 5.1 on 2024-08-21 21:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reviews", "0003_review_created_at_review_updated_at"),
    ]

    operations = [
        migrations.RenameField(
            model_name="review",
            old_name="user_id",
            new_name="user",
        ),
    ]
