import asyncio
import json

from channels.generic.websocket import AsyncWebsocketConsumer

from apps.messaging.auth import (
    get_user_from_scope,
    get_user_from_token,
    user_can_access_conversation_async,
)


class ChatConsumer(AsyncWebsocketConsumer):
    AUTH_TIMEOUT_SEC = 5

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"chat_{self.conversation_id}"
        self.user = None
        self.authed = False
        self._auth_task = None

        # Deprecated query-token fallback (one release)
        user = await get_user_from_scope(self.scope)
        if user:
            allowed = await user_can_access_conversation_async(user, self.conversation_id)
            if not allowed:
                await self.close(code=4003)
                return
            self.user = user
            self.authed = True
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            return

        await self.accept()
        self._auth_task = asyncio.create_task(self._auth_timeout())

    async def _auth_timeout(self):
        try:
            await asyncio.sleep(self.AUTH_TIMEOUT_SEC)
        except asyncio.CancelledError:
            return
        if not self.authed:
            await self.close(code=4001)

    async def disconnect(self, close_code):
        if self._auth_task:
            self._auth_task.cancel()
            self._auth_task = None
        if self.authed:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if self.authed:
            return
        if not text_data:
            await self.close(code=4001)
            return
        try:
            payload = json.loads(text_data)
        except (TypeError, json.JSONDecodeError):
            await self.close(code=4001)
            return
        if payload.get("type") != "auth" or not payload.get("token"):
            await self.close(code=4001)
            return

        user = await get_user_from_token(payload["token"])
        if not user:
            await self.close(code=4001)
            return
        allowed = await user_can_access_conversation_async(user, self.conversation_id)
        if not allowed:
            await self.close(code=4003)
            return

        self.user = user
        self.authed = True
        if self._auth_task:
            self._auth_task.cancel()
            self._auth_task = None
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({"type": "auth_ok"}))

    async def chat_message(self, event):
        if not self.authed:
            return
        await self.send(text_data=json.dumps({"type": "message", "data": event["message"]}))

    async def messages_read(self, event):
        if not self.authed:
            return
        await self.send(text_data=json.dumps({"type": "read", "data": event["data"]}))
