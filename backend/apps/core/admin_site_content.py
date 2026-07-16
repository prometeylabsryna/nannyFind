from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.cache import cache
from django.shortcuts import redirect, render
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldBooleanWidget

from apps.core.admin_utils import SingletonModelAdminMixin
from apps.core.block_defaults import (
    ACCENT_MARKER_KEYS,
    BLOCK_FIELD_LABELS,
    INLINE_KEYS,
    MULTILINE_KEYS,
    default_for_key,
    is_visibility_key,
)
from apps.core.block_field_help import field_help_for
from apps.core.admin_site_content_widgets import CmsAdminTextInputWidget, CmsAdminTextareaWidget
from apps.core.cms_accent import html_to_markers, markers_to_html
from apps.core.models import SiteBlock, SiteSettings
from apps.core.site_content_registry import SECTION_BY_SLUG, ContentSection

SITE_BLOCKS_CACHE_KEY = "pomich_site_blocks_v1"


def block_field_name(page: str, key: str) -> str:
    return f"block__{page}__{key}__text"


def _absolute_preview_url(preview_url: str) -> str:
    """`preview_url` у реєстрі — відносний шлях фронтенду (напр. "/", "/nanny/").

    Адмінка живе на окремому домені (api.*), тож без FRONTEND_URL браузер
    резолвив би шлях відносно поточного (api-)домену, де такого маршруту
    немає — звідси 404 на кнопці «Переглянути на сайті».
    """
    if not preview_url or preview_url.startswith(("http://", "https://")):
        return preview_url
    return f"{settings.FRONTEND_URL.rstrip('/')}{preview_url}"


def _widget_for_key(key: str):
    if key in INLINE_KEYS or key in ACCENT_MARKER_KEYS:
        return CmsAdminTextInputWidget()
    if key in MULTILINE_KEYS:
        return CmsAdminTextareaWidget(rows=4)
    return CmsAdminTextareaWidget(rows=2)


def _field_initial(key: str, raw: str) -> str:
    if key in ACCENT_MARKER_KEYS:
        return html_to_markers(raw)
    return raw


def _field_value_for_save(key: str, value: str) -> str:
    if key in ACCENT_MARKER_KEYS:
        return markers_to_html(value or "")
    return value or ""


class SitePageContentForm(forms.Form):
    section_visible = forms.BooleanField(
        required=False,
        label="Показувати цю секцію на сайті",
        widget=UnfoldBooleanWidget,
    )

    def __init__(self, section: ContentSection, blocks: dict[tuple[str, str], SiteBlock], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.section = section
        if section.visibility_key:
            vis_block = blocks.get((section.page_slug, section.visibility_key))
            self.fields["section_visible"].initial = (vis_block.text_html if vis_block else "1") not in {
                "0",
                "false",
                "",
            }

        for page, key in section.blocks:
            if section.visibility_key and key == section.visibility_key:
                continue
            label = BLOCK_FIELD_LABELS.get((page, key), key.replace("_", " ").capitalize())
            help_text = field_help_for(page, key)
            if is_visibility_key(key):
                field = forms.BooleanField(required=False, label=label, help_text=help_text, widget=UnfoldBooleanWidget())
                field.initial = blocks.get((page, key), None) and blocks[(page, key)].text_html not in {
                    "0",
                    "false",
                    "",
                }
            else:
                raw = blocks.get((page, key))
                initial = _field_initial(key, raw.text_html if raw else default_for_key(page, key))
                field = forms.CharField(
                    required=False,
                    label=label,
                    help_text=help_text,
                    widget=_widget_for_key(key),
                    initial=initial,
                )
            self.fields[block_field_name(page, key)] = field


def load_section_blocks(section: ContentSection) -> dict[tuple[str, str], SiteBlock]:
    result = {}
    for page, key in section.blocks:
        label = BLOCK_FIELD_LABELS.get((page, key), key)
        block, _ = SiteBlock.objects.get_or_create(
            page=page,
            key=key,
            defaults={
                "label": label,
                "text_html": default_for_key(page, key),
            },
        )
        result[(page, key)] = block
    return result


def _build_grouped_bound_fields(form, section: ContentSection) -> list[tuple[str, list]]:
    if section.field_groups:
        grouped: list[tuple[str, list[str]]] = []
        for group in section.field_groups:
            names = [block_field_name(section.page_slug, key) for key in group.keys]
            grouped.append((group.title, names))
    else:
        names = [
            block_field_name(page, key)
            for page, key in section.blocks
            if not (section.visibility_key and key == section.visibility_key)
        ]
        grouped = [("Контент", names)]

    return [
        (group_title, [form[field_name] for field_name in field_names if field_name in form.fields])
        for group_title, field_names in grouped
        if any(field_name in form.fields for field_name in field_names)
    ]


def site_content_section_view(request, section_slug: str, model_admin=None):
    section = SECTION_BY_SLUG[section_slug]
    blocks = load_section_blocks(section)

    if request.method == "POST":
        form = SitePageContentForm(section, blocks, request.POST)
        if form.is_valid():
            if section.visibility_key:
                vis = blocks[(section.page_slug, section.visibility_key)]
                vis.text_html = "1" if form.cleaned_data.get("section_visible") else "0"
                vis.save(update_fields=["text_html"])

            for page, key in section.blocks:
                if section.visibility_key and key == section.visibility_key:
                    continue
                fname = block_field_name(page, key)
                if fname not in form.cleaned_data:
                    continue
                value = form.cleaned_data[fname]
                block = blocks[(page, key)]
                if is_visibility_key(key):
                    block.text_html = "1" if value else "0"
                else:
                    block.text_html = _field_value_for_save(key, value)
                block.save(update_fields=["text_html"])

            cache.delete(SITE_BLOCKS_CACHE_KEY)
            messages.success(request, f"Збережено: {section.title}")
            return redirect(request.path)
        messages.error(request, "Перевірте форму — є помилки.")
    else:
        form = SitePageContentForm(section, blocks)

    context = {
        **admin.site.each_context(request),
        "form": form,
        "section": section,
        "grouped_bound_fields": _build_grouped_bound_fields(form, section),
        "title": section.title,
        "description": section.description,
        "opts": model_admin.model._meta if model_admin else SiteSettings._meta,
        "preview_url": _absolute_preview_url(section.preview_url),
    }
    return render(request, "admin/core/site_content_page.html", context)


class SiteContentSectionAdmin(SingletonModelAdminMixin, ModelAdmin):
    section_slug: str = ""

    def has_module_permission(self, request):
        return request.user.is_staff

    def changelist_view(self, request, extra_context=None):
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        return site_content_section_view(request, self.section_slug, model_admin=self)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return site_content_section_view(request, self.section_slug, model_admin=self)
