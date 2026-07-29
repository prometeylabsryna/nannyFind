from django.db import migrations


def update_legal_pages(apps, schema_editor):
    from apps.content.legal_page_skeletons import LEGAL_PAGES

    StaticPage = apps.get_model("content", "StaticPage")
    for page in LEGAL_PAGES:
        StaticPage.objects.update_or_create(
            key=page["key"],
            defaults={
                "title": page["title"],
                "body_html": page["body_html"],
                "is_published": True,
            },
        )


def noop(apps, schema_editor):
    """Не відкочуємо тексти — їх могли вже відредагувати в адмінці."""


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0002_seed_legal_static_pages"),
    ]

    operations = [
        migrations.RunPython(update_legal_pages, noop),
    ]
