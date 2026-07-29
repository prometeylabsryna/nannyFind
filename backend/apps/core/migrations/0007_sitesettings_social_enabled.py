from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_auto_catalog_trust_stats"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="facebook_enabled",
            field=models.BooleanField(default=True, verbose_name="Показувати Facebook"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="instagram_enabled",
            field=models.BooleanField(default=True, verbose_name="Показувати Instagram"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="tiktok_enabled",
            field=models.BooleanField(default=True, verbose_name="Показувати TikTok"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="telegram_enabled",
            field=models.BooleanField(default=True, verbose_name="Показувати Telegram"),
        ),
    ]
