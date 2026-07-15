from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.parents.models import ContactUnlock
from apps.payments.models import Payment, Subscription


class UnlockError(Exception):
    pass


def fulfill_payment(payment: Payment):
    if payment.status != Payment.Status.PAID:
        return
    if not hasattr(payment.user, "parent_profile"):
        return
    if Subscription.objects.filter(payment=payment).exists():
        return
    parent = payment.user.parent_profile
    plan = payment.plan

    sub = Subscription.objects.create(
        parent=parent,
        plan=plan,
        payment=payment,
        contacts_remaining=plan.contact_limit,
        status=Subscription.Status.ACTIVE,
    )
    if plan.city_access_days:
        sub.city_access_until = timezone.now() + timedelta(days=plan.city_access_days)
        sub.save(update_fields=["city_access_until"])


@transaction.atomic
def mark_payment_paid(payment: Payment, external_id: str = "", payload: dict | None = None):
    if payment.status == Payment.Status.PAID:
        return payment
    payment.status = Payment.Status.PAID
    payment.external_id = external_id
    payment.paid_at = timezone.now()
    if payload:
        payment.payload = payload
    payment.save()
    fulfill_payment(payment)
    return payment


def _active_subscriptions(parent):
    now = timezone.now()
    return Subscription.objects.filter(
        parent=parent,
        status=Subscription.Status.ACTIVE,
    ).filter(
        Q(contacts_remaining__gt=0) | Q(city_access_until__gt=now)
    )


def has_unlock_access(parent) -> bool:
    return _active_subscriptions(parent).exists()


def unlock_contact(parent, nanny) -> ContactUnlock:
    if ContactUnlock.objects.filter(parent=parent, nanny=nanny).exists():
        return ContactUnlock.objects.get(parent=parent, nanny=nanny)

    now = timezone.now()
    city_sub = (
        Subscription.objects.filter(
            parent=parent,
            status=Subscription.Status.ACTIVE,
            city_access_until__gt=now,
        )
        .order_by("-started_at")
        .first()
    )
    if city_sub:
        if not parent.city_id or not nanny.city_id or parent.city_id != nanny.city_id:
            raise UnlockError("Тариф «Місто» діє лише для нянь у вашому місті.")
        unlock, _ = ContactUnlock.objects.get_or_create(parent=parent, nanny=nanny)
        return unlock

    contact_sub = (
        Subscription.objects.filter(
            parent=parent,
            status=Subscription.Status.ACTIVE,
            contacts_remaining__gt=0,
        )
        .order_by("-started_at")
        .first()
    )
    if not contact_sub:
        raise UnlockError("Немає активної підписки або контактів.")
    contact_sub.contacts_remaining -= 1
    contact_sub.save(update_fields=["contacts_remaining"])
    unlock, _ = ContactUnlock.objects.get_or_create(parent=parent, nanny=nanny)
    return unlock
