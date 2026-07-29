from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from apps.core.admin_utils import ImagePreviewMixin, ReadOnlyTimestampsMixin, TinyMCEAdminMixin
from apps.nannies.models import AvailabilitySlot, NannyDocument, NannyProfile


class AvailabilityInline(TabularInline):
    model = AvailabilitySlot
    extra = 0
    fields = ("date", "status")


class DocumentInline(TabularInline):
    model = NannyDocument
    extra = 0
    fields = ("doc_type", "file", "status", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(NannyProfile)
class NannyProfileAdmin(TinyMCEAdminMixin, ImagePreviewMixin, ReadOnlyTimestampsMixin, ModelAdmin):
    tinymce_fields = ("description", "recommendations")
    list_display = (
        "first_name",
        "last_name",
        "city",
        "get_image_preview",
        "is_verified",
        "moderation_status",
        "rating_avg",
    )
    list_filter = ("city", "is_verified", "moderation_status")
    list_filter_submit = True
    search_fields = ("first_name", "last_name", "user__email")
    readonly_fields = ("get_image_preview", "rating_avg", "review_count", "created_at", "updated_at")
    autocomplete_fields = ("user", "city", "district")
    inlines = [DocumentInline, AvailabilityInline]
    fieldsets = (
        (
            "Основне",
            {"fields": ("user", "first_name", "last_name", "birth_date", "city", "district")},
        ),
        ("Профіль", {"fields": ("photo", "get_image_preview", "photo_url", "description", "hourly_rate")}),
        (
            "Досвід",
            {"fields": ("experience_years", "families_count", "languages", "certificates", "recommendations")},
        ),
        (
            "Переваги",
            {"fields": ("has_car", "medical_education", "first_aid_course")},
        ),
        (
            "Модерація",
            {
                "fields": ("is_verified", "moderation_status", "rating_avg", "review_count"),
                "description": (
                    "Рейтинг і кількість відгуків рахуються автоматично з опублікованих "
                    "відгуків (Адмінка → Відгуки). Не редагуються вручну."
                ),
            },
        ),
        ("Службове", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(NannyDocument)
class NannyDocumentAdmin(ModelAdmin):
    list_display = ("nanny", "doc_type", "status", "uploaded_at", "file_link")
    list_filter = ("doc_type", "status")
    list_filter_submit = True
    search_fields = ("nanny__first_name", "nanny__last_name", "nanny__user__email")
    readonly_fields = ("uploaded_at", "file_link")
    autocomplete_fields = ("nanny",)

    @admin.display(description="Файл")
    def file_link(self, obj):
        if not obj.file:
            return "—"
        return format_html('<a href="{}" target="_blank" rel="noopener">Відкрити</a>', obj.file.url)
