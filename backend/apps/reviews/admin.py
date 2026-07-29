from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.core.admin_utils import TinyMCEAdminMixin
from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ("text",)
    list_display = ("nanny", "parent", "rating", "is_published", "created_at")
    list_filter = ("rating", "is_published")
    list_filter_submit = True
    search_fields = ("nanny__first_name", "nanny__last_name", "parent__user__email", "text")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("parent", "nanny")
    list_editable = ("is_published",)
    fieldsets = (
        (
            None,
            {
                "fields": ("nanny", "parent", "rating", "text", "is_published", "created_at"),
                "description": (
                    "Опубліковані відгуки оновлюють рейтинг і лічильник у профілі няні "
                    "та на картках. Зніміть «Опубліковано», щоб приховати відгук."
                ),
            },
        ),
    )
