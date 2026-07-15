from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from apps.content.models import BlogPost, FAQItem, StaticPage
from apps.core.admin_utils import TinyMCEAdminMixin


@admin.register(BlogPost)
class BlogPostAdmin(TinyMCEAdminMixin, ModelAdmin):
    list_display = ("title", "slug", "category", "is_published", "published_at")
    list_filter = ("is_published", "category")
    list_filter_submit = True
    search_fields = ("title", "slug", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_published",)


@admin.register(FAQItem)
class FAQItemAdmin(ModelAdmin):
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
                "description": "Ключ сторінки фіксований. Текст зʼявиться на відповідній HTML-сторінці сайту.",
            },
        ),
        ("Контент сторінки", {"fields": ("body_html",)}),
        ("Службове", {"fields": ("updated_at",), "classes": ("collapse",)}),
    )
