from django.db import migrations

LEGAL_PAGES = [
    {
        "key": "public-offer",
        "title": "Публічна оферта",
        "body_html": (
            "<p>Публічна оферта платформи «Поміч поруч».</p>"
            "<p>1 контакт — 50 грн · 5 контактів — 200 грн · Місто 7 днів — 500 грн.</p>"
            '<div class="page-empty-hint"><span class="page-empty-hint-icon">📄</span>'
            "<span>Документ оновлюється відповідно до законодавства України та GDPR.</span></div>"
        ),
    },
    {
        "key": "terms-of-service",
        "title": "Умови використання",
        "body_html": (
            "<p>Ролі: гість (перегляд без реєстрації), батьки, помічники, адмін. "
            "Заборонено надавати неправдиві дані.</p>"
            '<div class="page-empty-hint"><span class="page-empty-hint-icon">📄</span>'
            "<span>Документ оновлюється відповідно до законодавства України та GDPR.</span></div>"
        ),
    },
    {
        "key": "privacy-policy",
        "title": "Політика конфіденційності",
        "body_html": (
            "<p>GDPR та ЗУ про захист персональних даних. Документи нянь — лише для адміна.</p>"
            '<div class="page-empty-hint"><span class="page-empty-hint-icon">📄</span>'
            "<span>Документ оновлюється відповідно до законодавства України та GDPR.</span></div>"
        ),
    },
    {
        "key": "cookie-policy",
        "title": "Політика cookies",
        "body_html": (
            "<p>Необхідні, аналітичні (GA4, Clarity), маркетингові (Meta Pixel).</p>"
            '<div class="page-empty-hint"><span class="page-empty-hint-icon">📄</span>'
            "<span>Документ оновлюється відповідно до законодавства України та GDPR.</span></div>"
        ),
    },
]


def seed_legal_pages(apps, schema_editor):
    StaticPage = apps.get_model("content", "StaticPage")
    for page in LEGAL_PAGES:
        StaticPage.objects.get_or_create(
            key=page["key"],
            defaults={
                "title": page["title"],
                "body_html": page["body_html"],
                "is_published": True,
            },
        )


def noop(apps, schema_editor):
    """Intentionally does nothing: rows may have been edited by an admin,
    so we don't want a migration rollback to delete real content."""


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_legal_pages, noop),
    ]
