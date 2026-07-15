from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_siteblock"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeHeroSettings",
            fields=[],
            options={
                "verbose_name": "Головна — Hero",
                "verbose_name_plural": "Головна — Hero",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.sitesettings",),
        ),
        migrations.CreateModel(
            name="HomeBenefitsSettings",
            fields=[],
            options={
                "verbose_name": "Головна — Переваги",
                "verbose_name_plural": "Головна — Переваги",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.sitesettings",),
        ),
        migrations.CreateModel(
            name="HomeStepsSettings",
            fields=[],
            options={
                "verbose_name": "Головна — Кроки",
                "verbose_name_plural": "Головна — Кроки",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.sitesettings",),
        ),
        migrations.CreateModel(
            name="HomeSectionsSettings",
            fields=[],
            options={
                "verbose_name": "Головна — Секції",
                "verbose_name_plural": "Головна — Секції",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.sitesettings",),
        ),
        migrations.CreateModel(
            name="SiteHeaderSettings",
            fields=[],
            options={
                "verbose_name": "Шапка сайту",
                "verbose_name_plural": "Шапка сайту",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.sitesettings",),
        ),
        migrations.CreateModel(
            name="SiteFooterSettings",
            fields=[],
            options={
                "verbose_name": "Підвал сайту",
                "verbose_name_plural": "Підвал сайту",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.sitesettings",),
        ),
        migrations.CreateModel(
            name="SiteCookieSettings",
            fields=[],
            options={
                "verbose_name": "Cookie-банер",
                "verbose_name_plural": "Cookie-банер",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.sitesettings",),
        ),
        migrations.CreateModel(
            name="CatalogUiSettings",
            fields=[],
            options={
                "verbose_name": "Каталог UI",
                "verbose_name_plural": "Каталог UI",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.sitesettings",),
        ),
        migrations.CreateModel(
            name="AuthPageSettings",
            fields=[],
            options={
                "verbose_name": "Auth тексти",
                "verbose_name_plural": "Auth тексти",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.sitesettings",),
        ),
    ]
