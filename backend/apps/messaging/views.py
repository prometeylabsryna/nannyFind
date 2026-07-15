from django.db.models import Count
from django.http import FileResponse, Http404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.messaging.access import conversations_for_user, get_user_conversation, is_platform_admin, user_can_access_conversation
from apps.messaging.attachments import make_attachment_token, verify_attachment_token
from apps.messaging.broadcast import broadcast_messages_read
from apps.messaging.models import Conversation, Message
from apps.messaging.serializers import ConversationSerializer, MessageCreateSerializer, MessageSerializer
from apps.nannies.models import NannyProfile

MESSAGES_PAGE_SIZE = 50


class ChatMessageThrottle(UserRateThrottle):
    scope = "chat_message"


def _blocked_response(user):
    if getattr(user, "status", None) == User.Status.BLOCKED:
        return Response({"detail": "Акаунт заблоковано."}, status=403)
    return None


class ConversationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return (
            conversations_for_user(self.request.user)
            .annotate(messages_count=Count("messages"))
            .order_by("-updated_at")
        )


class ConversationStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        blocked = _blocked_response(request.user)
        if blocked:
            return blocked

        user = request.user
        nanny_id = request.data.get("nanny_id")
        nanny = NannyProfile.objects.filter(pk=nanny_id).first()
        if not nanny:
            return Response({"detail": "Няню не знайдено."}, status=404)

        if user.role == User.Role.PARENT:
            parent = getattr(user, "parent_profile", None)
            if not parent:
                return Response({"detail": "Профіль батьків не знайдено."}, status=400)
            conv, _ = Conversation.objects.get_or_create(
                parent=parent,
                nanny=nanny,
            )
        elif is_platform_admin(user):
            conv, _ = Conversation.objects.get_or_create(
                admin_user=user,
                nanny=nanny,
                defaults={"parent": None},
            )
        else:
            return Response(
                {"detail": "Лише батьки та адміністратори можуть ініціювати чат."},
                status=403,
            )

        return Response(ConversationSerializer(conv, context={"request": request}).data)


class MessageListCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_throttles(self):
        if self.request.method == "POST":
            return [ChatMessageThrottle()]
        return []

    def get_conversation(self):
        return get_user_conversation(self.request.user, self.kwargs["conversation_id"])

    def get(self, request, *args, **kwargs):
        conv = self.get_conversation()
        if not conv:
            return Response({"detail": "Розмову не знайдено."}, status=404)

        qs = conv.messages.select_related("sender")
        before_raw = request.query_params.get("before_id")
        before_id = None
        if before_raw not in (None, ""):
            try:
                before_id = int(before_raw)
            except (TypeError, ValueError):
                return Response({"detail": "Некоректний before_id."}, status=400)
            qs = qs.filter(pk__lt=before_id)

        batch = list(qs.order_by("-id")[:MESSAGES_PAGE_SIZE])
        batch.reverse()
        has_more = bool(batch) and conv.messages.filter(pk__lt=batch[0].id).exists()

        data = MessageSerializer(batch, many=True, context={"request": request}).data
        if before_id is None:
            self._mark_incoming_read(conv, request.user)
        return Response({"results": data, "has_more": has_more})

    def post(self, request, *args, **kwargs):
        blocked = _blocked_response(request.user)
        if blocked:
            return blocked

        conv = self.get_conversation()
        if not conv:
            return Response({"detail": "Розмову не знайдено."}, status=404)
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attachment = serializer.validated_data.get("attachment")
        attachment_type = ""
        if attachment:
            if (attachment.content_type or "").startswith("image/"):
                attachment_type = "photo"
            else:
                attachment_type = "document"
        msg = Message.objects.create(
            conversation=conv,
            sender=request.user,
            text=serializer.validated_data.get("text", ""),
            attachment=attachment or "",
            attachment_type=attachment_type,
        )
        conv.save(update_fields=["updated_at"])
        return Response(
            MessageSerializer(msg, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def _mark_incoming_read(self, conv, user):
        unread = list(
            conv.messages.filter(is_read=False).exclude(sender=user).values_list("id", flat=True)
        )
        if not unread:
            return
        Message.objects.filter(pk__in=unread).update(is_read=True)
        broadcast_messages_read(conv.id, user.id, unread)


class MessageMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        blocked = _blocked_response(request.user)
        if blocked:
            return blocked

        conv = get_user_conversation(request.user, conversation_id)
        if not conv:
            return Response({"detail": "Розмову не знайдено."}, status=404)

        unread = list(
            conv.messages.filter(is_read=False)
            .exclude(sender=request.user)
            .values_list("id", flat=True)
        )
        if unread:
            Message.objects.filter(pk__in=unread).update(is_read=True)
            broadcast_messages_read(conv.id, request.user.id, unread)
        return Response({"marked": len(unread)})


class MessageAttachmentView(APIView):
    """Serve chat attachments via signed token or authenticated conversation access."""

    permission_classes = [AllowAny]

    def get(self, request, message_id):
        msg = Message.objects.select_related("conversation").filter(pk=message_id).first()
        if not msg or not msg.attachment:
            raise Http404()

        token = request.query_params.get("t") or ""
        allowed = False
        if request.user and request.user.is_authenticated:
            allowed = user_can_access_conversation(request.user, msg.conversation_id)
        if not allowed and token:
            allowed = verify_attachment_token(token, message_id)
        if not allowed:
            raise Http404()

        try:
            handle = msg.attachment.open("rb")
        except FileNotFoundError as exc:
            raise Http404() from exc

        filename = msg.attachment.name.rsplit("/", 1)[-1]
        return FileResponse(handle, as_attachment=False, filename=filename)


def deny_chat_media(request, path):
    """Block direct public access to chat/ media files in DEBUG."""
    if path.startswith("chat/"):
        raise Http404()
    from django.views.static import serve
    from django.conf import settings as dj_settings

    return serve(request, path, document_root=dj_settings.MEDIA_ROOT)
