# Generated by Django 5.1 on 2024-09-04 13:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("classes", "0020_remove_classimages_description_image_url_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="class",
            name="max_person",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="class",
            name="require_person",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
