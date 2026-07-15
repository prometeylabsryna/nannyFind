from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html


class ImagePreviewMixin:
    preview_field = "photo"
    preview_max_height = 80

    def get_image_preview(self, obj):
        url = self._preview_url(obj)
        if not url:
            return "—"
        return format_html(
            '<img src="{}" alt="" style="max-height:{}px;border-radius:6px">',
            url,
            self.preview_max_height,
        )

    get_image_preview.short_description = "Превʼю"

    def _preview_url(self, obj):
        field = getattr(obj, self.preview_field, None)
        if field and hasattr(field, "url"):
            return field.url
        return getattr(obj, "photo_url", "") or getattr(obj, "image_url", "")


class TinyMCEAdminMixin:
    tinymce_fields: tuple[str, ...] = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.tinymce_fields:
            from tinymce.widgets import TinyMCE

            kwargs["widget"] = TinyMCE()
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class SingletonModelAdminMixin:
    singleton_redirect_name = ""

    def has_add_permission(self, request) -> bool:
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = self.model.objects.get_or_create(pk=1)
        name = self.singleton_redirect_name or f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change"
        return HttpResponseRedirect(reverse(name, args=[obj.pk]))


class ReadOnlyTimestampsMixin:
    readonly_timestamp_fields = ("created_at", "updated_at", "uploaded_at")

    def get_readonly_fields(self, request, obj=None):
        base = list(super().get_readonly_fields(request, obj))
        for field in self.readonly_timestamp_fields:
            if hasattr(self.model, field) and field not in base:
                base.append(field)
        return base
