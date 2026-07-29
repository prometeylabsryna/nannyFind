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
        (
            "Соцмережі",
            {
                "fields": (
                    ("instagram_url", "instagram_enabled"),
                    ("facebook_url", "facebook_enabled"),
                    ("tiktok_url", "tiktok_enabled"),
                    ("telegram_url", "telegram_enabled"),
                ),
                "description": (
                    "URL зберігається навіть якщо галочку знято. "
                    "Без галочки іконка не показується на сайті."
                ),
            },
        ),
        (
            "SEO",
            {
                "fields": ("meta_description", "hero_trust_count", "hero_trust_cities"),
                "description": (
                    "Hero trust краще редагувати в «Головна — Hero». "
                    "Порожнє поле = автоцифри з каталогу; заповнене = ручний override."
                ),
            },
        ),
        ("Службове", {"fields": ("updated_at",)}),
    )
    readonly_fields = ("updated_at",)

