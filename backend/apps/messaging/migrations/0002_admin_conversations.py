# Generated manually for admin ↔ nanny chat

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("messaging", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="conversation",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="conversation",
            name="admin_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="admin_conversations",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Адміністратор",
            ),
        ),
        migrations.AlterField(
            model_name="conversation",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="conversations",
                to="parents.parentprofile",
            ),
        ),
        migrations.AddConstraint(
            model_name="conversation",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(("parent__isnull", False), ("admin_user__isnull", True))
                    | models.Q(("parent__isnull", True), ("admin_user__isnull", False))
                ),
                name="messaging_conversation_single_initiator",
            ),
        ),
        migrations.AddConstraint(
            model_name="conversation",
            constraint=models.UniqueConstraint(
                condition=models.Q(("parent__isnull", False)),
                fields=("parent", "nanny"),
                name="messaging_unique_parent_nanny",
            ),
        ),
        migrations.AddConstraint(
            model_name="conversation",
            constraint=models.UniqueConstraint(
                condition=models.Q(("admin_user__isnull", False)),
                fields=("admin_user", "nanny"),
                name="messaging_unique_admin_nanny",
            ),
        ),
    ]
