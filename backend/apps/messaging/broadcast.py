from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.messaging.serializers import attachment_api_url


def serialize_message(msg, request=None, viewer_id=None):
    from apps.messaging.serializers import MessageSerializer

    context = {}
    if request:
        context["request"] = request
    elif viewer_id is not None:
        context["viewer_id"] = viewer_id
    data = MessageSerializer(msg, context=context).data
    if msg.attachment and not data.get("attachment"):
        data["attachment"] = attachment_api_url(msg.id, request)
    return data


def broadcast_message(msg, request=None):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    payload = serialize_message(msg, request)
    async_to_sync(channel_layer.group_send)(
        f"chat_{msg.conversation_id}",
        {"type": "chat_message", "message": payload},
    )


def _conversation_participant_ids(conv):
    ids = set()
    if conv.nanny_id and conv.nanny.user_id:
        ids.add(conv.nanny.user_id)
    if conv.parent_id and conv.parent.user_id:
        ids.add(conv.parent.user_id)
    if conv.admin_user_id:
        ids.add(conv.admin_user_id)
    return ids


def broadcast_inbox_notification(msg):
    """Push a lightweight "new message" event to the recipient's personal
    inbox channel, so unread badges/popups update instantly even when the
    recipient isn't inside this specific conversation's thread."""
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    conv = msg.conversation
    recipients = _conversation_participant_ids(conv) - {msg.sender_id}
    if not recipients:
        return

    admin_label = ""
    if conv.admin_user_id:
        admin_label = conv.admin_user.get_full_name().strip() or "Адміністратор"

    data = {
        "conversation_id": conv.id,
        "nanny_name": str(conv.nanny),
        "parent_name": f"{admin_label} · Підтримка" if conv.admin_user_id else (str(conv.parent) if conv.parent_id else "Співрозмовник"),
        "conversation_type": "admin" if conv.admin_user_id else "parent",
        "text": msg.text,
        "attachment": bool(msg.attachment),
        "attachment_type": msg.attachment_type,
        "sender_id": msg.sender_id,
        "message_id": msg.id,
        "created_at": msg.created_at.isoformat(),
    }
    for user_id in recipients:
        async_to_sync(channel_layer.group_send)(
            f"inbox_{user_id}",
            {"type": "inbox_message", "data": data},
        )


def broadcast_messages_read(conversation_id, reader_id, message_ids):
    channel_layer = get_channel_layer()
    if not channel_layer or not message_ids:
        return
    async_to_sync(channel_layer.group_send)(
        f"chat_{conversation_id}",
        {
            "type": "messages_read",
            "data": {"reader_id": reader_id, "message_ids": message_ids},
        },
    )
