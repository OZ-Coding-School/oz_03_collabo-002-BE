# Generated by Django 5.1 on 2024-08-28 10:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("classes", "0009_class_class_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="classimages",
            name="image_url",
            field=models.CharField(),
        ),
    ]
