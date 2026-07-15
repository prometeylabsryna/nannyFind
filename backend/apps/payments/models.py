from django.conf import settings
from django.db import models

from apps.nannies.models import NannyProfile
from apps.parents.models import ParentProfile


class PricingPlan(models.Model):
    class PlanType(models.TextChoices):
        SINGLE = "single", "1 контакт"
        PACK5 = "pack5", "5 контактів"
        CITY7 = "city7", "Місто · 7 днів"

    code = models.CharField("Код", max_length=32, unique=True)
    title = models.CharField("Назва", max_length=128)
    description = models.TextField("Опис", blank=True)
    price_uah = models.PositiveIntegerField("Ціна ₴")
    plan_type = models.CharField("Тип", max_length=16, choices=PlanType.choices)
    contact_limit = models.PositiveSmallIntegerField("Контактів", default=1)
    city_access_days = models.PositiveSmallIntegerField("Днів доступу", default=0)
    is_featured = models.BooleanField("Featured", default=False)
    is_active = models.BooleanField("Активний", default=True)

    class Meta:
        ordering = ["price_uah"]
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифи"

    def __str__(self):
        return self.title


class Payment(models.Model):
    class Provider(models.TextChoices):
        LIQPAY = "liqpay", "LiqPay"
        WAYFORPAY = "wayforpay", "WayForPay"
        FONDY = "fondy", "Fondy"
        STUB = "stub", "Stub"

    class Status(models.TextChoices):
        PENDING = "pending", "Очікує"
        PAID = "paid", "Оплачено"
        FAILED = "failed", "Помилка"
        REFUNDED = "refunded", "Повернено"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    plan = models.ForeignKey(
        PricingPlan,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    provider = models.CharField("Провайдер", max_length=16, choices=Provider.choices)
    amount_uah = models.PositiveIntegerField("Сума ₴")
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    external_id = models.CharField("ID провайдера", max_length=255, blank=True)
    order_reference = models.CharField("Order ref", max_length=64, unique=True)
    payload = models.JSONField("Payload", default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Платіж"
        verbose_name_plural = "Платежі"


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активна"
        EXPIRED = "expired", "Завершена"
        CANCELLED = "cancelled", "Скасована"

    parent = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(
        PricingPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscription",
    )
    contacts_remaining = models.PositiveSmallIntegerField("Контактів залишилось", default=0)
    city_access_until = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Підписка"
        verbose_name_plural = "Підписки"
