from django.db import migrations, models

from apps.core.block_defaults import BLOCK_DEFAULTS, BLOCK_FIELD_LABELS, default_for_key


def seed_site_blocks(apps, schema_editor):
    SiteBlock = apps.get_model("core", "SiteBlock")
    for (page, key), default in BLOCK_DEFAULTS.items():
        SiteBlock.objects.get_or_create(
            page=page,
            key=key,
            defaults={
                "label": BLOCK_FIELD_LABELS.get((page, key), key),
                "text_html": default,
            },
        )


def unseed_site_blocks(apps, schema_editor):
    SiteBlock = apps.get_model("core", "SiteBlock")
    SiteBlock.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("page", models.CharField(choices=[("home", "Головна"), ("site", "Сайт"), ("catalog", "Каталог"), ("auth", "Auth")], max_length=32, verbose_name="Сторінка")),
                ("key", models.CharField(max_length=64, verbose_name="Ключ")),
                ("label", models.CharField(blank=True, max_length=128, verbose_name="Підпис")),
                ("content_type", models.CharField(choices=[("text", "Текст"), ("image", "Фото")], default="text", max_length=16, verbose_name="Тип")),
                ("text_html", models.TextField(blank=True, verbose_name="Текст")),
                ("image", models.ImageField(blank=True, upload_to="blocks/", verbose_name="Зображення")),
                ("sort_order", models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активний")),
            ],
            options={
                "verbose_name": "Блок контенту",
                "verbose_name_plural": "Блоки контенту",
                "ordering": ["page", "sort_order", "key"],
            },
        ),
        migrations.AddConstraint(
            model_name="siteblock",
            constraint=models.UniqueConstraint(fields=("page", "key"), name="unique_site_block_page_key"),
        ),
        migrations.RunPython(seed_site_blocks, unseed_site_blocks),
    ]
