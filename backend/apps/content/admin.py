from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.content.models import BlogPost, FAQItem, StaticPage
from apps.core.admin_utils import ImagePreviewMixin, TinyMCEAdminMixin


@admin.register(BlogPost)
class BlogPostAdmin(TinyMCEAdminMixin, ImagePreviewMixin, ModelAdmin):
    tinymce_fields = ("excerpt", "content")
    preview_field = "image"
    list_display = ("title", "slug", "category", "get_image_preview", "is_published", "published_at")
    list_filter = ("is_published", "category")
    list_filter_submit = True
    search_fields = ("title", "slug", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_published",)
    readonly_fields = ("get_image_preview",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "image",
                    "get_image_preview",
                    "image_url",
                    "image_alt",
                    "is_published",
                    "published_at",
                ),
                "description": (
                    "Завантажте обкладинку у полі «Зображення». "
                    "URL — запасний варіант, якщо файл не завантажено. "
                    "Alt-текст — опис обкладинки для скрінрідерів і SEO "
                    "(якщо порожньо, підставиться з заголовка). "
                    "Категорія — вільний текст (напр. Поради, Безпека)."
                ),
            },
        ),
        (
            "Текст статті",
            {
                "fields": ("excerpt", "content"),
                "description": (
                    "Короткий опис — для картки в списку блогу. "
                    "Контент — повний текст статті з форматуванням (TinyMCE)."
                ),
            },
        ),
    )


@admin.register(FAQItem)
class FAQItemAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ("answer",)
    list_display = ("question", "sort_order", "is_published")
    list_editable = ("sort_order", "is_published")
    search_fields = ("question", "answer")
    ordering = ("sort_order", "id")


@admin.register(StaticPage)
class StaticPageAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ("body_html",)
    list_display = ("key", "title", "is_published", "updated_at")
    list_filter = ("is_published",)
    list_filter_submit = True
    search_fields = ("title", "key")
    readonly_fields = ("updated_at",)
    fieldsets = (
        (
            None,
            {
                "fields": ("key", "title", "is_published"),
                "description": (
                    "Ключ сторінки фіксований (public-offer, terms-of-service, "
                    "privacy-policy, cookie-policy тощо). Текст зʼявиться на "
                    "відповідній сторінці сайту після збереження."
                ),
            },
        ),
        (
            "Контент сторінки",
            {
                "fields": ("body_html",),
                "description": (
                    "Замініть усі блоки [ЗАПОВНИТИ: …] на фінальний текст. "
                    "Каркас — лише шаблон; фінальну редакцію підтвердіть з юристом."
                ),
            },
        ),
        ("Службове", {"fields": ("updated_at",), "classes": ("collapse",)}),
    )
