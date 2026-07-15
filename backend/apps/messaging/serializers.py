from django.conf import settings
from rest_framework import serializers

from apps.messaging.attachments import make_attachment_token
from apps.messaging.models import Conversation, Message

MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024
MAX_MESSAGE_TEXT_LENGTH = 4000
ALLOWED_ATTACHMENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/heic",
    "image/heif",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".heic",
    ".heif",
    ".pdf",
    ".doc",
    ".docx",
}


def attachment_api_url(message_id, request=None) -> str:
    token = make_attachment_token(message_id)
    path = f"/api/v1/chat/messages/{message_id}/attachment/?t={token}"
    if request is not None:
        return request.build_absolute_uri(path)
    base = getattr(settings, "BACKEND_URL", "").rstrip("/")
    return f"{base}{path}" if base else path


class MessageSerializer(serializers.ModelSerializer):
    is_own = serializers.SerializerMethodField()
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)
    attachment = serializers.SerializerMethodField()
    attachment_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "sender_id",
            "text",
            "attachment",
            "attachment_name",
            "attachment_type",
            "is_own",
            "is_read",
            "created_at",
        )
        read_only_fields = ("id", "sender_id", "created_at", "attachment_type", "is_read")

    def get_is_own(self, obj):
        request = self.context.get("request")
        if request and getattr(request, "user", None) and request.user.is_authenticated:
            return obj.sender_id == request.user.id
        viewer_id = self.context.get("viewer_id")
        if viewer_id is not None:
            return obj.sender_id == viewer_id
        return False

    def get_attachment(self, obj):
        if not obj.attachment:
            return None
        return attachment_api_url(obj.id, self.context.get("request"))

    def get_attachment_name(self, obj):
        if not obj.attachment:
            return ""
        return obj.attachment.name.rsplit("/", 1)[-1]


class ConversationSerializer(serializers.ModelSerializer):
    nanny_name = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    conversation_type = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    messages_count = serializers.SerializerMethodField()

    def get_nanny_name(self, obj):
        return str(obj.nanny)

    def get_parent_name(self, obj):
        if obj.admin_user_id:
            admin = obj.admin_user
            label = admin.get_full_name().strip() or "Адміністратор"
            return f"{label} · Підтримка"
        if obj.parent_id:
            return str(obj.parent)
        return "Співрозмовник"

    def get_conversation_type(self, obj):
        return "admin" if obj.admin_user_id else "parent"

    class Meta:
        model = Conversation
        fields = (
            "id",
            "nanny",
            "parent",
            "conversation_type",
            "nanny_name",
            "parent_name",
            "last_message",
            "unread_count",
            "messages_count",
            "updated_at",
        )

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if not msg:
            return None
        return MessageSerializer(msg, context=self.context).data

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()

    def get_messages_count(self, obj):
        if hasattr(obj, "messages_count"):
            return obj.messages_count
        return obj.messages.count()


class MessageCreateSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=False, allow_blank=True, max_length=MAX_MESSAGE_TEXT_LENGTH)

    class Meta:
        model = Message
        fields = ("text", "attachment")

    def validate(self, attrs):
        text = (attrs.get("text") or "").strip()
        attachment = attrs.get("attachment")
        if not text and not attachment:
            raise serializers.ValidationError("Додайте текст або файл.")
        if len(text) > MAX_MESSAGE_TEXT_LENGTH:
            raise serializers.ValidationError(
                {"text": f"Текст задовгий (макс. {MAX_MESSAGE_TEXT_LENGTH} символів)."}
            )
        attrs["text"] = text
        return attrs

    def validate_attachment(self, attachment):
        if not attachment:
            return attachment
        if attachment.size > MAX_ATTACHMENT_SIZE:
            raise serializers.ValidationError("Файл завеликий (макс. 20 МБ).")
        content_type = getattr(attachment, "content_type", "") or ""
        if content_type not in ALLOWED_ATTACHMENT_TYPES:
            raise serializers.ValidationError("Недозволений тип файлу.")
        name = (getattr(attachment, "name", "") or "").lower()
        if not any(name.endswith(ext) for ext in ALLOWED_ATTACHMENT_EXTENSIONS):
            raise serializers.ValidationError("Недозволене розширення файлу.")
        return attachment
