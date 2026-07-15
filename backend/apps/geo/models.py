from django.db import models


class City(models.Model):
    name = models.CharField("Місто", max_length=64, unique=True)
    slug = models.SlugField("Slug", max_length=64, unique=True)
    is_active = models.BooleanField("Активне", default=True)
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Місто"
        verbose_name_plural = "Міста"

    def __str__(self):
        return self.name


class District(models.Model):
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="districts",
        verbose_name="Місто",
    )
    name = models.CharField("Район", max_length=128)
    slug = models.SlugField("Slug", max_length=128)

    class Meta:
        ordering = ["name"]
        unique_together = [("city", "slug")]
        verbose_name = "Район"
        verbose_name_plural = "Райони"

    def __str__(self):
        return f"{self.city.name}, {self.name}"
