from django.conf import settings
from django.db import models

from apps.geo.models import City
from apps.nannies.models import NannyProfile


class ParentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="parent_profile",
    )
    first_name = models.CharField("Ім'я", max_length=64, blank=True)
    last_name = models.CharField("Прізвище", max_length=64, blank=True)
    birth_date = models.DateField("Дата народження", null=True, blank=True)
    photo = models.ImageField("Фото", upload_to="parents/photos/", blank=True)
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parents",
        verbose_name="Місто",
    )
    children_count = models.PositiveSmallIntegerField("Кількість дітей", default=0)
    children_ages = models.CharField("Вік дітей", max_length=128, blank=True)
    special_needs = models.TextField("Особливі потреби", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профіль батьків"
        verbose_name_plural = "Профілі батьків"

    def __str__(self):
        return f"{self.last_name} {self.first_name}".strip() or self.user.email

    @property
    def display_photo(self):
        if self.photo:
            return self.photo.url
        return ""


class Favorite(models.Model):
    parent = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    nanny = models.ForeignKey(
        NannyProfile,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("parent", "nanny")]
        ordering = ["-created_at"]
        verbose_name = "Обране"
        verbose_name_plural = "Обране"


class ContactUnlock(models.Model):
    parent = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        related_name="contact_unlocks",
    )
    nanny = models.ForeignKey(
        NannyProfile,
        on_delete=models.CASCADE,
        related_name="contact_unlocks",
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("parent", "nanny")]
        verbose_name = "Відкритий контакт"
        verbose_name_plural = "Відкриті контакти"
