from django.conf import settings
from django.db import models

from apps.nannies.models import NannyProfile
from apps.parents.models import ParentProfile


class Conversation(models.Model):
    parent = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True,
    )
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_conversations",
        null=True,
        blank=True,
        verbose_name="Адміністратор",
    )
    nanny = models.ForeignKey(
        NannyProfile,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Розмова"
        verbose_name_plural = "Розмови"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(parent__isnull=False, admin_user__isnull=True)
                    | models.Q(parent__isnull=True, admin_user__isnull=False)
                ),
                name="messaging_conversation_single_initiator",
            ),
            models.UniqueConstraint(
                fields=["parent", "nanny"],
                condition=models.Q(parent__isnull=False),
                name="messaging_unique_parent_nanny",
            ),
            models.UniqueConstraint(
                fields=["admin_user", "nanny"],
                condition=models.Q(admin_user__isnull=False),
                name="messaging_unique_admin_nanny",
            ),
        ]


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    text = models.TextField("Текст", blank=True)
    attachment = models.FileField("Вкладення", upload_to="chat/", blank=True)
    attachment_type = models.CharField("Тип вкладення", max_length=16, blank=True)
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"
