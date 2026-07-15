from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.core.admin_site_content_proxies import register_site_content_section_admins
from apps.core.admin_utils import SingletonModelAdminMixin
from apps.core.models import SiteSettings

register_site_content_section_admins()


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdminMixin, ModelAdmin):
    singleton_redirect_name = "admin:core_sitesettings_change"
    fieldsets = (
        (
            "Основне",
            {
                "fields": ("site_name", "support_phone", "support_email", "support_address", "work_hours"),
                "description": "Глобальні контакти та назва. Email/телефон у підвалі — у розділі «Підвал».",
            },
        ),
        ("Соцмережі", {"fields": ("instagram_url", "facebook_url", "tiktok_url", "telegram_url")}),
        (
            "SEO",
            {
                "fields": ("meta_description", "hero_trust_count", "hero_trust_cities"),
                "description": "Hero trust — дубль у «Головна — Hero», якщо потрібен один source правди.",
            },
        ),
        ("Службове", {"fields": ("updated_at",)}),
    )
    readonly_fields = ("updated_at",)

