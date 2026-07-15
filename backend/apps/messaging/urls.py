from django.urls import path

from apps.messaging.views import (
    ConversationListView,
    ConversationStartView,
    MessageAttachmentView,
    MessageListCreateView,
    MessageMarkReadView,
)

urlpatterns = [
    path("conversations/", ConversationListView.as_view(), name="conversation-list"),
    path("conversations/start/", ConversationStartView.as_view(), name="conversation-start"),
    path(
        "conversations/<int:conversation_id>/messages/",
        MessageListCreateView.as_view(),
        name="message-list-create",
    ),
    path(
        "conversations/<int:conversation_id>/read/",
        MessageMarkReadView.as_view(),
        name="message-mark-read",
    ),
    path(
        "messages/<int:message_id>/attachment/",
        MessageAttachmentView.as_view(),
        name="message-attachment",
    ),
]
