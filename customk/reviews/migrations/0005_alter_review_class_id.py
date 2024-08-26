# Generated by Django 5.1 on 2024-08-22 05:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("classes", "0008_rename_course_classdate_class_id_and_more"),
        ("reviews", "0004_rename_user_id_review_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="class_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews",
                to="classes.class",
            ),
        ),
    ]