from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsParent
from apps.nannies.models import NannyProfile
from apps.payments.models import Payment, PricingPlan, Subscription
from apps.payments.providers import PaymentProviderError, get_provider, get_webhook_provider, list_available_providers, new_order_reference
from apps.payments.serializers import CheckoutSerializer, PaymentSerializer, PricingPlanSerializer, SubscriptionSerializer
from apps.payments.services import UnlockError, has_unlock_access, mark_payment_paid, unlock_contact


class PricingPlanListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PricingPlanSerializer
    queryset = PricingPlan.objects.filter(is_active=True)
    pagination_class = None


class PaymentProviderListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from django.conf import settings

        providers = list_available_providers()
        return Response(
            {
                "providers": providers,
                "stub_mode": settings.PAYMENTS_STUB_MODE,
                "default_provider": next((p["code"] for p in providers if p.get("default")), "liqpay"),
            }
        )


class CheckoutView(APIView):
    permission_classes = [IsParent]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = PricingPlan.objects.filter(code=serializer.validated_data["plan_code"], is_active=True).first()
        if not plan:
            return Response({"detail": "Тариф не знайдено."}, status=404)
        provider_name = serializer.validated_data["provider"]
        try:
            provider = get_provider(provider_name)
        except PaymentProviderError as exc:
            return Response({"detail": str(exc)}, status=503)

        payment = Payment.objects.create(
            user=request.user,
            plan=plan,
            provider=provider.code if provider.code != "stub" else Payment.Provider.STUB,
            amount_uah=plan.price_uah,
            order_reference=new_order_reference(),
        )
        try:
            checkout = provider.create_checkout(payment)
        except PaymentProviderError as exc:
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status"])
            return Response({"detail": str(exc)}, status=502)
        return Response({"payment": PaymentSerializer(payment).data, "checkout": checkout})


class PaymentHistoryView(generics.ListAPIView):
    permission_classes = [IsParent]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related("plan")


class SubscriptionListView(generics.ListAPIView):
    permission_classes = [IsParent]
    serializer_class = SubscriptionSerializer
    pagination_class = None

    def get_queryset(self):
        return Subscription.objects.filter(parent=self.request.user.parent_profile).select_related("plan")


class UnlockContactView(APIView):
    permission_classes = [IsParent]

    def post(self, request):
        nanny_id = request.data.get("nanny_id")
        nanny = NannyProfile.objects.filter(pk=nanny_id).select_related("user", "city").first()
        if not nanny:
            return Response({"detail": "Няню не знайдено."}, status=404)
        parent = request.user.parent_profile
        from apps.parents.models import ContactUnlock

        if ContactUnlock.objects.filter(parent=parent, nanny=nanny).exists():
            return Response({"phone": nanny.user.phone, "unlocked": True})
        if not has_unlock_access(parent):
            return Response({"detail": "Немає активної підписки або контактів."}, status=402)
        try:
            unlock_contact(parent, nanny)
        except UnlockError as exc:
            return Response({"detail": str(exc)}, status=402)
        return Response({"phone": nanny.user.phone, "unlocked": True})


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    provider_code = ""

    def post(self, request, provider=None):
        code = provider or self.provider_code
        try:
            provider_obj = get_webhook_provider(code)
            result = provider_obj.verify_webhook(request)
        except PaymentProviderError as exc:
            return Response({"detail": str(exc)}, status=400)
        payment = Payment.objects.filter(order_reference=result["order_reference"]).first()
        if not payment:
            return Response({"detail": "Payment not found."}, status=404)
        if result["status"] == "paid":
            mark_payment_paid(payment, result.get("external_id", ""), result.get("payload"))
        elif result["status"] == "failed":
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status"])
        webhook_response = provider_obj.build_webhook_response(result)
        if webhook_response:
            return Response(webhook_response)
        return Response({"status": "ok"})


class StubConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.conf import settings

        if not settings.PAYMENTS_STUB_MODE:
            return Response({"detail": "Тестовий режим оплати вимкнено."}, status=403)
        order = request.data.get("order_reference")
        payment = Payment.objects.filter(order_reference=order, user=request.user).first()
        if not payment:
            return Response({"detail": "Платіж не знайдено."}, status=404)
        mark_payment_paid(payment, external_id=f"stub-{order}")
        return Response(PaymentSerializer(payment).data)
