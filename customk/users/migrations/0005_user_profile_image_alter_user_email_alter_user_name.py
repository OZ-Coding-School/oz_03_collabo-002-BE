# Generated by Django 5.1 on 2024-08-28 06:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_alter_user_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="profile_image",
            field=models.URLField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(editable=False, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="name",
            field=models.CharField(max_length=50),
        ),
    ]
