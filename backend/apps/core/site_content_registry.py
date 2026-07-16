from dataclasses import dataclass, field

from django.urls import reverse_lazy


@dataclass(frozen=True)
class FieldGroup:
    title: str
    keys: tuple[str, ...]


@dataclass(frozen=True)
class ContentSection:
    slug: str
    page_slug: str
    title: str
    blocks: tuple[tuple[str, str], ...]
    sidebar_title: str = ""
    sidebar_icon: str = "edit_note"
    preview_url: str = "/"
    description: str = ""
    visibility_key: str = ""
    field_groups: tuple[FieldGroup, ...] = field(default_factory=tuple)
    sidebar_group: str = ""
    admin_model_name: str = ""


def _blocks(page: str, *keys: str) -> tuple[tuple[str, str], ...]:
    return tuple((page, key) for key in keys)


CONTENT_SECTIONS: tuple[ContentSection, ...] = (
    ContentSection(
        slug="hero",
        page_slug="home",
        title="Головна — Hero",
        sidebar_title="Головна — Hero",
        sidebar_icon="home",
        preview_url="/",
        description="Перший екран головної сторінки: заголовок, форма пошуку няні та бейдж довіри.",
        visibility_key="hero_section_visible",
        sidebar_group="home",
        blocks=_blocks(
            "home",
            "hero_section_visible",
            "hero_title_html",
            "hero_subtitle",
            "search_city_label",
            "search_date_label",
            "search_format_label",
            "search_submit",
            "hero_image",
            "hero_image_alt",
            "hero_trust_icon",
            "hero_trust_count",
            "hero_trust_cities",
        ),
        admin_model_name="homeherosettings",
        field_groups=(
            FieldGroup("Заголовок і текст", ("hero_title_html", "hero_subtitle")),
            FieldGroup("Форма пошуку", ("search_city_label", "search_date_label", "search_format_label", "search_submit")),
            FieldGroup("Фото та довіра", ("hero_image", "hero_image_alt", "hero_trust_icon", "hero_trust_count", "hero_trust_cities")),
        ),
    ),
    ContentSection(
        slug="benefits",
        page_slug="home",
        title="Головна — Переваги",
        sidebar_title="Головна — Переваги",
        sidebar_icon="verified",
        preview_url="/#benefits",
        description="4 картки переваг під Hero на головній.",
        visibility_key="benefits_section_visible",
        sidebar_group="home",
        admin_model_name="homebenefitssettings",
        blocks=_blocks(
            "home",
            "benefits_section_visible",
            "benefit_1_icon",
            "benefit_1_title",
            "benefit_1_text",
            "benefit_2_icon",
            "benefit_2_title",
            "benefit_2_text",
            "benefit_3_icon",
            "benefit_3_title",
            "benefit_3_text",
            "benefit_4_icon",
            "benefit_4_title",
            "benefit_4_text",
        ),
        field_groups=tuple(
            FieldGroup(f"Перевага {i}", (f"benefit_{i}_icon", f"benefit_{i}_title", f"benefit_{i}_text"))
            for i in range(1, 5)
        ),
    ),
    ContentSection(
        slug="steps",
        page_slug="home",
        title="Головна — Як працює",
        sidebar_title="Головна — Кроки",
        sidebar_icon="format_list_numbered",
        preview_url="/#steps",
        description="Секція з 4 кроками на головній і на сторінці «Як це працює».",
        visibility_key="steps_section_visible",
        sidebar_group="home",
        admin_model_name="homestepssettings",
        blocks=_blocks(
            "home",
            "steps_section_visible",
            "steps_title",
            "steps_subtitle",
            "step_1_title",
            "step_1_desc",
            "step_2_title",
            "step_2_desc",
            "step_3_title",
            "step_3_desc",
            "step_4_title",
            "step_4_desc",
        ),
        field_groups=(
            FieldGroup("Заголовки секції", ("steps_title", "steps_subtitle")),
            FieldGroup("Крок 1", ("step_1_title", "step_1_desc")),
            FieldGroup("Крок 2", ("step_2_title", "step_2_desc")),
            FieldGroup("Крок 3", ("step_3_title", "step_3_desc")),
            FieldGroup("Крок 4", ("step_4_title", "step_4_desc")),
        ),
    ),
    ContentSection(
        slug="sections",
        page_slug="home",
        title="Головна — Інші блоки",
        sidebar_title="Головна — Секції",
        sidebar_icon="view_carousel",
        preview_url="/",
        description="Блоки внизу головної: популярні няні, міста та кнопка внизу екрана на мобільних.",
        sidebar_group="home",
        admin_model_name="homesectionssettings",
        blocks=_blocks(
            "home",
            "featured_section_visible",
            "featured_title",
            "featured_cta",
            "cities_section_visible",
            "cities_title",
            "city_kyiv_label",
            "city_lviv_label",
            "city_dnipro_label",
            "sticky_cta_label",
        ),
        field_groups=(
            FieldGroup("Популярні няні", ("featured_section_visible", "featured_title", "featured_cta")),
            FieldGroup("Міста", ("cities_section_visible", "cities_title", "city_kyiv_label", "city_lviv_label", "city_dnipro_label")),
            FieldGroup("Кнопка внизу екрана", ("sticky_cta_label",)),
        ),
    ),
    ContentSection(
        slug="header",
        page_slug="site",
        title="Шапка сайту",
        sidebar_title="Шапка",
        sidebar_icon="web_asset",
        preview_url="/",
        description="Назва бренду, пункти меню та кнопки у верхній частині кожної сторінки.",
        sidebar_group="site",
        admin_model_name="siteheadersettings",
        blocks=_blocks(
            "site",
            "header_brand_uk",
            "header_nav_home",
            "header_nav_how",
            "header_nav_catalog",
            "header_nav_blog",
            "header_nav_faq",
            "header_nav_contacts",
            "header_btn_search",
            "header_btn_register",
            "header_btn_login",
            "header_mobile_menu",
        ),
        field_groups=(
            FieldGroup("Бренд", ("header_brand_uk",)),
            FieldGroup("Меню", ("header_nav_home", "header_nav_how", "header_nav_catalog", "header_nav_blog", "header_nav_faq", "header_nav_contacts")),
            FieldGroup("Кнопки", ("header_btn_search", "header_btn_register", "header_btn_login", "header_mobile_menu")),
        ),
    ),
    ContentSection(
        slug="footer",
        page_slug="site",
        title="Підвал сайту",
        sidebar_title="Підвал",
        sidebar_icon="bottom_navigation",
        preview_url="/",
        description="Тексти внизу кожної сторінки: бренд, посилання, контакти.",
        sidebar_group="site",
        admin_model_name="sitefootersettings",
        blocks=_blocks(
            "site",
            "footer_brand_uk",
            "footer_desc",
            "footer_col_nav",
            "footer_col_legal",
            "footer_col_contacts",
            "footer_link_contact",
            "footer_link_services",
            "footer_email",
            "footer_phone",
            "footer_copyright",
            "footer_tech",
        ),
        field_groups=(
            FieldGroup("Бренд", ("footer_brand_uk", "footer_desc")),
            FieldGroup("Колонки", ("footer_col_nav", "footer_col_legal", "footer_col_contacts")),
            FieldGroup("Посилання та контакти", ("footer_link_contact", "footer_link_services", "footer_email", "footer_phone")),
            FieldGroup("Низ", ("footer_copyright", "footer_tech")),
        ),
    ),
    ContentSection(
        slug="cookie",
        page_slug="site",
        title="Cookie-банер",
        sidebar_title="Cookies",
        sidebar_icon="cookie",
        preview_url="/",
        description="Тексти спливаючого вікна про cookies при першому відвідуванні.",
        sidebar_group="site",
        admin_model_name="sitecookiesettings",
        blocks=_blocks(
            "site",
            "cookie_title",
            "cookie_body",
            "cookie_body_link",
            "cookie_accept",
            "cookie_reject",
            "cookie_settings",
            "cookie_save",
            "cookie_toggle_necessary",
            "cookie_toggle_analytics",
            "cookie_toggle_marketing",
        ),
        field_groups=(
            FieldGroup("Банер", ("cookie_title", "cookie_body", "cookie_body_link")),
            FieldGroup("Кнопки", ("cookie_accept", "cookie_reject", "cookie_settings", "cookie_save")),
            FieldGroup("Перемикачі", ("cookie_toggle_necessary", "cookie_toggle_analytics", "cookie_toggle_marketing")),
        ),
    ),
    ContentSection(
        slug="catalog",
        page_slug="catalog",
        title="Каталог — підписи",
        sidebar_title="Каталог UI",
        sidebar_icon="manage_search",
        preview_url="/nanny/",
        description="Заголовки та підписи на сторінці пошуку нянь.",
        sidebar_group="pages",
        admin_model_name="cataloguisettings",
        blocks=_blocks("catalog", "catalog_title", "catalog_subtitle", "catalog_filters_title", "catalog_filters_toggle"),
        field_groups=(
            FieldGroup("Заголовки", ("catalog_title", "catalog_subtitle")),
            FieldGroup("Фільтри", ("catalog_filters_title", "catalog_filters_toggle")),
        ),
    ),
    ContentSection(
        slug="auth",
        page_slug="auth",
        title="Вхід та реєстрація",
        sidebar_title="Вхід / Реєстрація",
        sidebar_icon="login",
        preview_url="/login.html",
        description="Тексти на сторінках входу та створення акаунта.",
        sidebar_group="pages",
        admin_model_name="authpagesettings",
        blocks=_blocks(
            "auth",
            "auth_trust_1",
            "auth_trust_2",
            "auth_trust_3",
            "auth_login_title",
            "auth_login_divider",
            "auth_login_submit",
            "auth_login_footer",
            "auth_register_title",
            "auth_register_submit",
            "auth_register_footer",
        ),
        field_groups=(
            FieldGroup("Бейджі довіри", ("auth_trust_1", "auth_trust_2", "auth_trust_3")),
            FieldGroup("Вхід", ("auth_login_title", "auth_login_divider", "auth_login_submit", "auth_login_footer")),
            FieldGroup("Реєстрація", ("auth_register_title", "auth_register_submit", "auth_register_footer")),
        ),
    ),
)

SECTION_BY_SLUG = {section.slug: section for section in CONTENT_SECTIONS}

SIDEBAR_GROUP_LABELS: tuple[tuple[str, str], ...] = (
    ("home", "Головна сторінка"),
    ("site", "Шапка та підвал"),
    ("pages", "Окремі сторінки"),
)


def iter_section_blocks(section: ContentSection) -> tuple[tuple[str, str], ...]:
    return section.blocks


def _sidebar_item(section: ContentSection) -> dict:
    return {
        "title": section.sidebar_title or section.title,
        "icon": section.sidebar_icon,
        "link": reverse_lazy(f"admin:core_{section.admin_model_name}_changelist"),
    }


def build_content_sidebar_items() -> list[dict]:
    return [_sidebar_item(section) for section in CONTENT_SECTIONS]


def build_content_sidebar_navigation_groups() -> list[dict]:
    groups: list[dict] = []
    for group_key, group_title in SIDEBAR_GROUP_LABELS:
        items = [_sidebar_item(section) for section in CONTENT_SECTIONS if section.sidebar_group == group_key]
        if items:
            groups.append({"title": group_title, "separator": True, "items": items})
    ungrouped = [_sidebar_item(section) for section in CONTENT_SECTIONS if not section.sidebar_group]
    if ungrouped:
        groups.append({"title": "Тексти сайту", "separator": True, "items": ungrouped})
    return groups
