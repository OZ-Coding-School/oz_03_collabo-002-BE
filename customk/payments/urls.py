from django.urls import re_path

from .views import payment, paypal, referral

urlpatterns = [
    re_path(r"^paypal/orders/?$", paypal.create_order, name="create-paypal-order"),
    re_path(
        r"^paypal/orders/(?P<order_id>[A-Za-z0-9]+)/capture/?$",
        paypal.capture_order,
        name="capture-paypal-order",
    ),
    re_path(
        r"^paypal/refund/(?P<payment_id>\d+)/?$",
        paypal.refund_order,
        name="refund-paypal-order",
    ),
    re_path(
        r"^referral/?$",
        referral.ReferralView.as_view(),
        name="referral-view",
    ),
    re_path(r"^$", payment.PaymentView.as_view(), name="payments-view"),
]
