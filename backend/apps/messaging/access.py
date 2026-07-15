from apps.accounts.models import User
from apps.messaging.models import Conversation


def is_platform_admin(user):
    return bool(
        user
        and user.is_authenticated
        and (user.role == User.Role.ADMIN or user.is_staff or user.is_superuser)
    )


def conversations_for_user(user):
    qs = Conversation.objects.select_related("parent", "nanny", "admin_user")
    if user.role == User.Role.PARENT:
        return qs.filter(parent=user.parent_profile)
    if user.role == User.Role.NANNY:
        return qs.filter(nanny=user.nanny_profile)
    if is_platform_admin(user):
        return qs.filter(admin_user=user)
    return Conversation.objects.none()


def get_user_conversation(user, conversation_id):
    qs = Conversation.objects.filter(pk=conversation_id)
    if user.role == User.Role.PARENT:
        return qs.filter(parent=user.parent_profile).first()
    if user.role == User.Role.NANNY:
        return qs.filter(nanny=user.nanny_profile).first()
    if is_platform_admin(user):
        return qs.filter(admin_user=user).first()
    return None


def user_can_access_conversation(user, conversation_id):
    return get_user_conversation(user, conversation_id) is not None
