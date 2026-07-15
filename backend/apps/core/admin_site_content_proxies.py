from django.contrib import admin

from apps.core.admin_site_content import SiteContentSectionAdmin
from apps.core.models import (
    AuthPageSettings,
    CatalogUiSettings,
    HomeBenefitsSettings,
    HomeHeroSettings,
    HomeSectionsSettings,
    HomeStepsSettings,
    SiteCookieSettings,
    SiteFooterSettings,
    SiteHeaderSettings,
)

_SECTION_ADMINS = (
    (HomeHeroSettings, "hero"),
    (HomeBenefitsSettings, "benefits"),
    (HomeStepsSettings, "steps"),
    (HomeSectionsSettings, "sections"),
    (SiteHeaderSettings, "header"),
    (SiteFooterSettings, "footer"),
    (SiteCookieSettings, "cookie"),
    (CatalogUiSettings, "catalog"),
    (AuthPageSettings, "auth"),
)


def register_site_content_section_admins():
    for model, slug in _SECTION_ADMINS:
        admin_cls = type(
            f"{model.__name__}Admin",
            (SiteContentSectionAdmin,),
            {"section_slug": slug},
        )
        if not admin.site.is_registered(model):
            admin.site.register(model, admin_cls)
