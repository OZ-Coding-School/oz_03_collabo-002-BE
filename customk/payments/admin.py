from django.contrib import admin

from payments.models import Payment, ReferralCode


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):  # type: ignore
    pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "status",
        "amount",
        "refunded_amount",
        "currency",
        "payment_method",
        "payer_email",
        "user_id",
        "class_id",
        "class_date_id",
        "quantity",
        "referral_code",
        "transaction_id",
    )
    search_fields = ("order_id", "payment_method", "payer_email", "transaction_id")
    list_filter = ("status", "currency", "payment_method")
    readonly_fields = [field.name for field in Payment._meta.fields]
