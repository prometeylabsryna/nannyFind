from django.urls import path

from apps.payments.views import (
    CheckoutView,
    PaymentHistoryView,
    PaymentProviderListView,
    PaymentWebhookView,
    PricingPlanListView,
    StubConfirmView,
    SubscriptionListView,
    UnlockContactView,
)

urlpatterns = [
    path("plans/", PricingPlanListView.as_view(), name="payment-plans"),
    path("providers/", PaymentProviderListView.as_view(), name="payment-providers"),
    path("checkout/", CheckoutView.as_view(), name="payment-checkout"),
    path("history/", PaymentHistoryView.as_view(), name="payment-history"),
    path("subscriptions/", SubscriptionListView.as_view(), name="subscription-list"),
    path("unlock/", UnlockContactView.as_view(), name="contact-unlock"),
    path("stub/confirm/", StubConfirmView.as_view(), name="payment-stub-confirm"),
    path("webhooks/<str:provider>/", PaymentWebhookView.as_view(), name="payment-webhook"),
]
