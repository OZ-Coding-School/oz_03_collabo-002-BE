# Generated by Django 5.1 on 2024-09-08 12:36

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0003_auto_20240906_1550"),
        ("payments", "0002_payment_refunded_amount"),
        ("questions", "0006_remove_question_answer_user_id_alter_question_answer"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Notification",
            new_name="PaymentNotification",
        ),
        migrations.RemoveField(
            model_name="paymentnotification",
            name="question",
        ),
        migrations.AddField(
            model_name="paymentnotification",
            name="payment",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                to="payments.payment",
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="QuestionNotification",
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
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("message", models.CharField(max_length=255)),
                ("is_read", models.BooleanField(default=False)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="questions.question",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]