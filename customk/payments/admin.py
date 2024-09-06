from django.contrib import admin

from payments.models import ReferralCode


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):  # type: ignore
    pass
