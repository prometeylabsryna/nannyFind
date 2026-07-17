from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.messaging.broadcast import broadcast_inbox_notification, broadcast_message
from apps.messaging.models import Message


@receiver(post_save, sender=Message)
def on_message_created(sender, instance, created, **kwargs):
    if created:
        broadcast_message(instance)
        broadcast_inbox_notification(instance)
