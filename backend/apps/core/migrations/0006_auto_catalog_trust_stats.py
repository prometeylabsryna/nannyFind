from django.db import migrations, models


def clear_stale_trust_copy(apps, schema_editor):
    SiteBlock = apps.get_model("core", "SiteBlock")
    SiteBlock.objects.filter(page="home", key__in=["hero_trust_count", "hero_trust_cities"]).update(
        text_html=""
    )
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.all().update(hero_trust_count="", hero_trust_cities="")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_sitesettings_tiktok_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="hero_trust_count",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Порожньо = авто з каталогу. Або свій текст (override).",
                max_length=32,
                verbose_name="Hero: кількість нянь",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="hero_trust_cities",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Порожньо = авто з каталогу. Або свій текст (override).",
                max_length=64,
                verbose_name="Hero: міста",
            ),
        ),
        migrations.RunPython(clear_stale_trust_copy, noop),
    ]
