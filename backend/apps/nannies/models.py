from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.geo.models import City, District


class NannyProfile(models.Model):
    class ModerationStatus(models.TextChoices):
        DRAFT = "draft", "Чернетка"
        PENDING = "pending", "На модерації"
        APPROVED = "approved", "Схвалено"
        REJECTED = "rejected", "Відхилено"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nanny_profile",
    )
    first_name = models.CharField("Ім'я", max_length=64)
    last_name = models.CharField("Прізвище", max_length=64, blank=True)
    birth_date = models.DateField("Дата народження", null=True, blank=True)
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="nannies",
        verbose_name="Місто",
    )
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nannies",
        verbose_name="Район",
    )
    photo = models.ImageField("Фото", upload_to="nannies/photos/", blank=True)
    photo_url = models.URLField("URL фото", blank=True)
    description = models.TextField("Опис", blank=True)
    hourly_rate = models.PositiveIntegerField("Ставка ₴/год", default=300)
    experience_years = models.PositiveSmallIntegerField("Роки досвіду", default=0)
    families_count = models.PositiveSmallIntegerField("Сім'ї", default=0)
    recommendations = models.TextField("Рекомендації", blank=True)
    languages = models.JSONField("Мови", default=list, blank=True)
    certificates = models.JSONField("Сертифікати", default=list, blank=True)
    has_car = models.BooleanField("Має авто", default=False)
    medical_education = models.BooleanField("Медична освіта", default=False)
    first_aid_course = models.BooleanField("Курс першої допомоги", default=False)
    is_verified = models.BooleanField("Перевірено", default=False)
    moderation_status = models.CharField(
        "Модерація",
        max_length=16,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
    )
    rating_avg = models.DecimalField(
        "Рейтинг",
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    review_count = models.PositiveIntegerField("Відгуки", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-rating_avg", "-review_count"]
        verbose_name = "Профіль няні"
        verbose_name_plural = "Профілі нянь"
        indexes = [
            models.Index(fields=["city", "is_verified"]),
            models.Index(fields=["moderation_status"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def age(self):
        if not self.birth_date:
            return None
        from datetime import date

        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def display_photo(self):
        if self.photo:
            return self.photo.url
        return self.photo_url


class AvailabilitySlot(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Доступна"
        BUSY = "busy", "Зайнята"
        VACATION = "vacation", "Відпустка"

    nanny = models.ForeignKey(
        NannyProfile,
        on_delete=models.CASCADE,
        related_name="availability",
    )
    date = models.DateField("Дата")
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    class Meta:
        unique_together = [("nanny", "date")]
        ordering = ["date"]
        verbose_name = "Доступність"
        verbose_name_plural = "Доступність"


class NannyDocument(models.Model):
    class DocType(models.TextChoices):
        PASSPORT = "passport", "Паспорт"
        IPN = "ipn", "ІПН"
        FIRST_AID = "first_aid", "Сертифікат першої допомоги"
        MEDICAL_CERT = "medical_cert", "Медичний сертифікат"
        EDUCATION_CERT = "education_cert", "Освітній / педагогічний"
        CRIMINAL_RECORD = "criminal_record", "Довідка про несудимість"
        OTHER = "other", "Інший документ"

    class DocStatus(models.TextChoices):
        PENDING = "pending", "Очікує"
        APPROVED = "approved", "OK"
        REJECTED = "rejected", "Відхилено"

    nanny = models.ForeignKey(
        NannyProfile,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    doc_type = models.CharField("Тип", max_length=32, choices=DocType.choices)
    file = models.FileField("Файл", upload_to="nannies/documents/")
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=DocStatus.choices,
        default=DocStatus.PENDING,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("nanny", "doc_type")]
        verbose_name = "Документ"
        verbose_name_plural = "Документи"
