from django.db import migrations


def fix_brand_spelling(apps, schema_editor):
    SiteBlock = apps.get_model("core", "SiteBlock")
    for block in SiteBlock.objects.all():
        text = block.text_html or ""
        new_text = (
            text.replace("Поміч poruch", "Поміч поруч")
            .replace("Поміч порuch", "Поміч поруч")
            .replace("порuch", "поруч")
        )
        if new_text != text:
            block.text_html = new_text
            block.save(update_fields=["text_html"])

    SiteSettings = apps.get_model("core", "SiteSettings")
    for settings in SiteSettings.objects.all():
        name = settings.site_name or ""
        new_name = (
            name.replace("Поміч poruch", "Поміч поруч")
            .replace("Поміч порuch", "Поміч поруч")
            .replace("порuch", "поруч")
        )
        if new_name != name:
            settings.site_name = new_name
            settings.save(update_fields=["site_name"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_cms_proxy_models"),
    ]

    operations = [
        migrations.RunPython(fix_brand_spelling, migrations.RunPython.noop),
    ]
