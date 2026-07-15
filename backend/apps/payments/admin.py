from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.payments.models import Payment, PricingPlan, Subscription


@admin.register(PricingPlan)
class PricingPlanAdmin(ModelAdmin):
    list_display = ("code", "title", "price_uah", "plan_type", "is_active", "is_featured")
    list_editable = ("is_active", "is_featured")
    search_fields = ("code", "title")


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ("order_reference", "user", "amount_uah", "provider", "status", "created_at")
    list_filter = ("provider", "status")
    list_filter_submit = True
    search_fields = ("order_reference", "user__email", "external_id")
    readonly_fields = ("order_reference", "external_id", "created_at", "paid_at")
    autocomplete_fields = ("user",)


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ("parent", "plan", "contacts_remaining", "status", "started_at", "expires_at")
    list_filter = ("status", "plan")
    list_filter_submit = True
    search_fields = ("parent__user__email",)
    autocomplete_fields = ("parent", "plan")
