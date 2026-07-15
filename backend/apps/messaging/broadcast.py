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
