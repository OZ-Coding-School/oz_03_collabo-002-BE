# Generated by Django 5.1 on 2024-08-16 14:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Class",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=400)),
                ("description", models.TextField(blank=True)),
                ("max_person", models.IntegerField(default=0)),
                ("require_person", models.IntegerField(default=0)),
                ("price", models.IntegerField(default=0)),
                ("address", models.TextField(default="")),
            ],
        ),
        migrations.CreateModel(
            name="ClassDate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dates",
                        to="classes.class",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ClassImages",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image_url", models.URLField(max_length=2000)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="classes.class",
                    ),
                ),
            ],
        ),
    ]
