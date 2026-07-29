import json

from django.db import migrations, models
from django.utils.html import escape


def _paragraphs_to_html(value) -> str:
    if value is None or value == "" or value == []:
        return ""
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "".join(f"<p>{escape(part)}</p>" for part in parts)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return ""
        if stripped.startswith("["):
            try:
                return _paragraphs_to_html(json.loads(stripped))
            except json.JSONDecodeError:
                return value
        return value
    return escape(str(value))


def forwards(apps, schema_editor):
    BlogPost = apps.get_model("content", "BlogPost")
    for post in BlogPost.objects.all().iterator():
        post.content_html = _paragraphs_to_html(post.content)
        post.save(update_fields=["content_html"])


def backwards(apps, schema_editor):
    BlogPost = apps.get_model("content", "BlogPost")
    for post in BlogPost.objects.all().iterator():
        html = (post.content_html or "").strip()
        post.content = [html] if html else []
        post.save(update_fields=["content"])


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0003_update_legal_static_pages"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="content_html",
            field=models.TextField(blank=True, default="", verbose_name="Контент"),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(model_name="blogpost", name="content"),
        migrations.RenameField(
            model_name="blogpost",
            old_name="content_html",
            new_name="content",
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="content",
            field=models.TextField(blank=True, verbose_name="Контент"),
        ),
    ]
