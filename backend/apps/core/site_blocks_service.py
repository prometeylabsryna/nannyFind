from django.core.cache import cache

from apps.core.admin_site_content import SITE_BLOCKS_CACHE_KEY
from apps.core.block_defaults import default_for_key
from apps.core.models import SiteBlock, SiteSettings

SITE_BLOCKS_CACHE_TTL = 60


def _block_value(block: SiteBlock) -> str:
    if block.content_type == SiteBlock.ContentType.IMAGE:
        return block.image.url if block.image else ""
    return block.text_html


def get_all_site_content() -> dict:
    cached = cache.get(SITE_BLOCKS_CACHE_KEY)
    if cached is not None:
        return cached

    blocks = {}
    for block in SiteBlock.objects.filter(is_active=True):
        blocks[block.cache_key] = _block_value(block)

    settings = SiteSettings.get_solo()
    payload = {
        "blocks": blocks,
        "settings": {
            "site_name": settings.site_name,
            "support_phone": settings.support_phone,
            "support_email": settings.support_email,
            "support_address": settings.support_address,
            "work_hours": settings.work_hours,
            "facebook_url": settings.facebook_url,
            "instagram_url": settings.instagram_url,
            "tiktok_url": settings.tiktok_url,
            "telegram_url": settings.telegram_url,
            "meta_description": settings.meta_description,
        },
    }
    cache.set(SITE_BLOCKS_CACHE_KEY, payload, SITE_BLOCKS_CACHE_TTL)
    return payload


def get_block_text(page: str, key: str, blocks: dict | None = None, fallback: str = "") -> str:
    if blocks is None:
        blocks = get_all_site_content().get("blocks", {})
    return blocks.get(f"{page}.{key}", fallback or default_for_key(page, key))


def is_section_visible(page: str, visibility_key: str, blocks: dict | None = None) -> bool:
    value = get_block_text(page, visibility_key, blocks=blocks, fallback="1")
    return value not in {"0", "false", "False", ""}
