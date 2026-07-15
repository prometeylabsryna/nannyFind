from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.nannies.models import NannyProfile
from apps.parents.models import ParentProfile


class Review(models.Model):
    parent = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )
    nanny = models.ForeignKey(
        NannyProfile,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        "Оцінка",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    text = models.TextField("Коментар", blank=True)
    is_published = models.BooleanField("Опубліковано", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("parent", "nanny")]
        ordering = ["-created_at"]
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
