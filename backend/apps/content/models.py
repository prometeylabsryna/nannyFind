from django.db import models


class BlogPost(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Slug", unique=True)
    excerpt = models.TextField("Короткий опис", blank=True)
    content = models.TextField("Контент", blank=True)
    category = models.CharField("Категорія", max_length=64, blank=True)
    image = models.ImageField("Зображення", upload_to="blog/covers/", blank=True)
    image_url = models.URLField("URL зображення", blank=True)
    image_alt = models.CharField(
        "Alt-текст обкладинки",
        max_length=255,
        blank=True,
        help_text='Опис зображення для доступності та SEO. Якщо порожньо — «Ілюстрація до статті «{заголовок}»».',
    )
    is_published = models.BooleanField("Опубліковано", default=False)
    published_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Стаття блогу"
        verbose_name_plural = "Статті блогу"

    def __str__(self):
        return self.title

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url

    @property
    def display_image_alt(self):
        alt = (self.image_alt or "").strip()
        if alt:
            return alt
        title = (self.title or "").strip()
        if title:
            return f"Ілюстрація до статті «{title}»"
        return "Ілюстрація до статті блогу"


class FAQItem(models.Model):
    question = models.CharField("Питання", max_length=512)
    answer = models.TextField("Відповідь")
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубліковано", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"


class StaticPage(models.Model):
    class PageKey(models.TextChoices):
        HOW_IT_WORKS = "how-it-works", "Як це працює"
        SERVICES = "services", "Послуги"
        PUBLIC_OFFER = "public-offer", "Публічна оферта"
        TERMS = "terms-of-service", "Умови використання"
        PRIVACY = "privacy-policy", "Політика конфіденційності"
        COOKIE = "cookie-policy", "Політика cookies"
        CONTACTS = "contacts", "Контакти"

    key = models.CharField("Ключ", max_length=64, choices=PageKey.choices, unique=True)
    title = models.CharField("Заголовок", max_length=255)
    body_html = models.TextField("HTML контент", blank=True)
    is_published = models.BooleanField("Опубліковано", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Статична сторінка"
        verbose_name_plural = "Статичні сторінки"
