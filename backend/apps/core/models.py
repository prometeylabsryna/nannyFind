from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField("Назва сайту", max_length=128, default="Поміч поруч")
    support_phone = models.CharField("Телефон підтримки", max_length=32, blank=True)
    support_email = models.EmailField("Email підтримки", blank=True)
    support_address = models.CharField("Адреса", max_length=255, blank=True)
    work_hours = models.CharField("Години роботи", max_length=128, blank=True)
    facebook_url = models.URLField("Facebook", blank=True)
    facebook_enabled = models.BooleanField("Показувати Facebook", default=True)
    instagram_url = models.URLField("Instagram", blank=True)
    instagram_enabled = models.BooleanField("Показувати Instagram", default=True)
    tiktok_url = models.URLField("TikTok", blank=True)
    tiktok_enabled = models.BooleanField("Показувати TikTok", default=True)
    telegram_url = models.URLField("Telegram", blank=True)
    telegram_enabled = models.BooleanField("Показувати Telegram", default=True)
    meta_description = models.TextField("Meta description", blank=True)
    hero_trust_count = models.CharField(
        "Hero: кількість нянь",
        max_length=32,
        blank=True,
        default="",
        help_text="Порожньо = авто з каталогу. Або свій текст (override).",
    )
    hero_trust_cities = models.CharField(
        "Hero: міста",
        max_length=64,
        blank=True,
        default="",
        help_text="Порожньо = авто з каталогу. Або свій текст (override).",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Налаштування сайту"
        verbose_name_plural = "Налаштування сайту"

    def __str__(self):
        return self.site_name

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteBlock(models.Model):
    class Page(models.TextChoices):
        HOME = "home", "Головна"
        SITE = "site", "Сайт"
        CATALOG = "catalog", "Каталог"
        AUTH = "auth", "Auth"

    class ContentType(models.TextChoices):
        TEXT = "text", "Текст"
        IMAGE = "image", "Фото"

    page = models.CharField("Сторінка", max_length=32, choices=Page.choices)
    key = models.CharField("Ключ", max_length=64)
    label = models.CharField("Підпис", max_length=128, blank=True)
    content_type = models.CharField(
        "Тип",
        max_length=16,
        choices=ContentType.choices,
        default=ContentType.TEXT,
    )
    text_html = models.TextField("Текст", blank=True)
    image = models.ImageField("Зображення", upload_to="blocks/", blank=True)
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активний", default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["page", "key"], name="unique_site_block_page_key"),
        ]
        ordering = ["page", "sort_order", "key"]
        verbose_name = "Блок контенту"
        verbose_name_plural = "Блоки контенту"

    def __str__(self):
        return f"{self.page}.{self.key}"

    @property
    def cache_key(self) -> str:
        return f"{self.page}.{self.key}"


class HomeHeroSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Головна — Hero"
        verbose_name_plural = "Головна — Hero"


class HomeBenefitsSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Головна — Переваги"
        verbose_name_plural = "Головна — Переваги"


class HomeStepsSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Головна — Кроки"
        verbose_name_plural = "Головна — Кроки"


class HomeSectionsSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Головна — Секції"
        verbose_name_plural = "Головна — Секції"


class SiteHeaderSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Шапка сайту"
        verbose_name_plural = "Шапка сайту"


class SiteFooterSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Підвал сайту"
        verbose_name_plural = "Підвал сайту"


class SiteCookieSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Cookie-банер"
        verbose_name_plural = "Cookie-банер"


class CatalogUiSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Каталог UI"
        verbose_name_plural = "Каталог UI"


class AuthPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Auth тексти"
        verbose_name_plural = "Auth тексти"
