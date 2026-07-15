from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from apps.messaging.access import user_can_access_conversation

UserModel = get_user_model()


def _token_from_scope(scope):
    """Deprecated: JWT in query string. Prefer auth message after connect."""
    query = parse_qs(scope.get("query_string", b"").decode())
    token = (query.get("token") or [None])[0]
    if token:
        return token
    headers = dict(scope.get("headers") or [])
    auth = headers.get(b"authorization", b"").decode()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


def user_from_access_token(token_str):
    if not token_str:
        return None
    try:
        token = AccessToken(token_str)
        return UserModel.objects.get(pk=token["user_id"])
    except (InvalidToken, TokenError, UserModel.DoesNotExist, KeyError):
        return None


@database_sync_to_async
def get_user_from_scope(scope):
    return user_from_access_token(_token_from_scope(scope))


@database_sync_to_async
def get_user_from_token(token_str):
    return user_from_access_token(token_str)


@database_sync_to_async
def user_can_access_conversation_async(user, conversation_id):
    return user_can_access_conversation(user, conversation_id)
