from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parents", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="parentprofile",
            name="birth_date",
            field=models.DateField(blank=True, null=True, verbose_name="Дата народження"),
        ),
        migrations.AddField(
            model_name="parentprofile",
            name="photo",
            field=models.ImageField(blank=True, upload_to="parents/photos/", verbose_name="Фото"),
        ),
    ]
