# Generated by Django 5.1 on 2024-08-21 07:44

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("classes", "0004_class_created_at_class_updated_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="class",
            name="address",
            field=models.JSONField(
                blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder
            ),
        ),
    ]