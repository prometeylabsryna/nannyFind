from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0005_blogpost_image_upload"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="image_alt",
            field=models.CharField(
                blank=True,
                help_text=(
                    "Опис зображення для доступності та SEO. "
                    "Якщо порожньо — «Ілюстрація до статті «{заголовок}»»."
                ),
                max_length=255,
                verbose_name="Alt-текст обкладинки",
            ),
        ),
    ]
