from rest_framework import serializers

from apps.payments.models import Payment, PricingPlan, Subscription


class PricingPlanSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="code")
    price = serializers.IntegerField(source="price_uah")
    desc = serializers.CharField(source="description")
    featured = serializers.BooleanField(source="is_featured")

    class Meta:
        model = PricingPlan
        fields = ("id", "title", "price", "desc", "featured", "plan_type", "contact_limit")


class CheckoutSerializer(serializers.Serializer):
    plan_code = serializers.CharField()
    provider = serializers.ChoiceField(
        choices=("liqpay", "wayforpay", "fondy", "stub"),
        default="liqpay",
    )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "plan", "provider", "amount_uah", "status", "order_reference", "created_at", "paid_at")


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PricingPlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id",
            "plan",
            "contacts_remaining",
            "city_access_until",
            "status",
            "started_at",
            "expires_at",
        )
