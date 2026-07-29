from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0004_blogpost_content_to_html"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="image",
            field=models.ImageField(
                blank=True,
                upload_to="blog/covers/",
                verbose_name="Зображення",
            ),
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="image_url",
            field=models.URLField(blank=True, verbose_name="URL зображення"),
        ),
    ]
