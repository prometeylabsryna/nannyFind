from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_fix_brand_spelling"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="tiktok_url",
            field=models.URLField(blank=True, verbose_name="TikTok"),
        ),
    ]
