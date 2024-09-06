import logging
import uuid

from django.db import transaction
from rest_framework import serializers

from payments.models import Payment
from payments.services import (
    add_class_date_person,
    expire_referral_code,
    verify_referral_code,
)

logger = logging.getLogger(__name__)


class BasePaymentSerializer(serializers.ModelSerializer):
    class_title = serializers.SerializerMethodField()
    class_date_info = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = (
            "order_id",
            "user_id",
            "capture_id",
            "status",
            "amount",
            "currency",
            "payer_email",
            "transaction_id",
            "payment_method",
            "refunded_amount",
            "created_at",
            "class_title",
            "class_date_info",
        )

    def get_class_title(self, obj) -> str | None:
        return obj.related_class.title if obj.related_class else None

    def get_class_date_info(self, obj):
        if obj.related_class_date:
            return {
                "start_date": obj.related_class_date.start_date,
                "start_time": obj.related_class_date.start_time,
                "end_time": obj.related_class_date.end_time,
            }
        return None

    def payment_process(self, class_date_id, person, code):
        logger.info("start payment_process")
        if not add_class_date_person(class_date_id, person):
            logger.warning(f"add_class_date_person failed {class_date_id, person}")
            raise serializers.ValidationError("클래스 인원 추가 실패")

        if code is None:
            return

        if verify_referral_code(code) is None:
            logger.warning(f"verify_referral_code failed {code}")
            raise serializers.ValidationError("유효하지 않은 코드입니다")

        if not expire_referral_code(code):
            logger.warning(f"expire_referral_code failed {code}")
            raise serializers.ValidationError("이미 만료된 코드입니다")


class PaymentPayPalSerializer(BasePaymentSerializer):
    @transaction.atomic
    def create(self, validated_data):
        paypal_data = self.context.get("paypal_data", {})
        class_date_id = validated_data.get("class_date_id", None)
        person = validated_data.get("quantity", 0)
        referral_code = validated_data.get("referral_code", None)

        payment_data = {
            "order_id": paypal_data.get("id"),
            "capture_id": paypal_data["purchase_units"][0]["payments"]["captures"][0][
                "id"
            ],
            "status": paypal_data.get("status"),
            "amount": paypal_data["purchase_units"][0]["payments"]["captures"][0][
                "amount"
            ]["value"],
            "currency": paypal_data["purchase_units"][0]["payments"]["captures"][0][
                "amount"
            ]["currency_code"],
            "payer_email": paypal_data["payer"]["email_address"],
            "transaction_id": paypal_data["purchase_units"][0]["payments"]["captures"][
                0
            ].get("id"),
            "payment_method": "paypal",
            **validated_data,
        }

        self.payment_process(class_date_id, person, referral_code)

        return super().create(payment_data)


class PaymentPostAPISerializer(BasePaymentSerializer):
    @transaction.atomic
    def create(self, validated_data):
        class_date_id = validated_data.get("class_date_id", None)
        person = validated_data.get("quantity", 0)
        referral_code = validated_data.get("referral_code", None)
        payer_email = self.context.get("payer_email", "")

        payment_data = {
            "order_id": str(uuid.uuid4()).replace("-", ""),
            "status": "completed",
            "amount": 0,
            "currency": "FREE",
            "payer_email": payer_email,
            "payment_method": "none",
            **validated_data,
        }

        self.payment_process(class_date_id, person, referral_code)

        return super().create(payment_data)


class RefundSuccessResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="환불 성공 메시지")
    refund_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, help_text="환불된 금액"
    )
