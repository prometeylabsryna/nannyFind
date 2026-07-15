from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.messaging.models import Conversation, Message


class MessageInline(TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("sender", "text", "attachment", "created_at", "is_read")


@admin.register(Conversation)
class ConversationAdmin(ModelAdmin):
    inlines = [MessageInline]
    list_display = ("parent", "admin_user", "nanny", "updated_at")
    search_fields = ("parent__user__email", "admin_user__email", "nanny__user__email")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("parent", "nanny", "admin_user")
