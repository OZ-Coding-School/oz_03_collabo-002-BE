from django.contrib import admin

from .models import PaymentNotification, QuestionNotification


@admin.register(QuestionNotification)
class QuestionNotificationAdmin(admin.ModelAdmin):
    list_display = ("message", "class_field", "created_at", "is_read")
    list_filter = ("is_read", "question__class_id")
    search_fields = ("message", "question__class_id__title")

    def class_field(self, obj):
        return obj.question.class_id.title

    class_field.admin_order_field = "question__class_id__title"  # type: ignore
    class_field.short_description = "Class Title"  # type: ignore


@admin.register(PaymentNotification)
class PaymentNotificationAdmin(admin.ModelAdmin):
    list_display = ("message", "payment_method", "created_at", "is_read")
    list_filter = ("is_read", "payment__payment_method")
    search_fields = ("message", "payment__order_id")

    def payment_method(self, obj):
        return obj.payment.payment_method

    payment_method.admin_order_field = "payment__payment_method"  # type: ignore
    payment_method.short_description = "Payment Method"  # type: ignore
