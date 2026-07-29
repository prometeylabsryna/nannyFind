from django.core.cache import cache
from django.db import migrations

NEW = "Сайт від PrometeyLabs"
CACHE_KEY = "pomich_site_blocks_v1"


def update_footer_tech(apps, schema_editor):
    SiteBlock = apps.get_model("core", "SiteBlock")
    qs = SiteBlock.objects.filter(page="site", key="footer_tech")
    for block in qs:
        text = (block.text_html or "").strip()
        if text == NEW:
            continue
        if "HTMX" in text or "HTML" in text or not text:
            block.text_html = NEW
            block.save(update_fields=["text_html"])
    if not qs.exists():
        SiteBlock.objects.create(
            page="site",
            key="footer_tech",
            label="Кредит студії",
            text_html=NEW,
        )
    try:
        cache.delete(CACHE_KEY)
    except Exception:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_sitesettings_social_enabled"),
    ]

    operations = [
        migrations.RunPython(update_footer_tech, migrations.RunPython.noop),
    ]
