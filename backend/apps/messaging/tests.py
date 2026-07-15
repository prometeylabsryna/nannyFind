from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, TransactionTestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.geo.models import City
from apps.messaging.models import Conversation, Message
from apps.nannies.models import NannyProfile
from apps.parents.models import ParentProfile


class MessagingAPITest(TestCase):
    def setUp(self):
        self.city = City.objects.create(name="Київ", slug="kyiv")
        self.parent_user = User.objects.create_user(
            username="parent_chat",
            email="parent_chat@test.ua",
            password="SecurePass123!",
            role=User.Role.PARENT,
            status=User.Status.ACTIVE,
        )
        self.parent_profile = ParentProfile.objects.create(
            user=self.parent_user,
            first_name="Батько",
            last_name="Тест",
        )
        self.nanny_user = User.objects.create_user(
            username="nanny_chat",
            email="nanny_chat@test.ua",
            password="SecurePass123!",
            role=User.Role.NANNY,
            status=User.Status.ACTIVE,
        )
        self.nanny_profile = NannyProfile.objects.create(
            user=self.nanny_user,
            first_name="Няня",
            last_name="Тест",
            city=self.city,
            moderation_status=NannyProfile.ModerationStatus.APPROVED,
            is_verified=True,
        )
        self.other_parent = User.objects.create_user(
            username="other_parent",
            email="other_parent@test.ua",
            password="SecurePass123!",
            role=User.Role.PARENT,
            status=User.Status.ACTIVE,
        )
        ParentProfile.objects.create(user=self.other_parent, first_name="Інший")

        self.parent_client = APIClient()
        self.nanny_client = APIClient()
        self.other_client = APIClient()
        self._login(self.parent_client, "parent_chat@test.ua")
        self._login(self.nanny_client, "nanny_chat@test.ua")
        self._login(self.other_client, "other_parent@test.ua")

    def _login(self, client, email):
        res = client.post(
            "/api/v1/auth/login/",
            {"email": email, "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.content)
        token = res.json()["tokens"]["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _start(self, client=None):
        client = client or self.parent_client
        res = client.post(
            "/api/v1/chat/conversations/start/",
            {"nanny_id": self.nanny_profile.id},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.content)
        return res.json()

    def test_parent_starts_conversation(self):
        data = self._start()
        self.assertEqual(data["nanny"], self.nanny_profile.id)
        self.assertEqual(data["conversation_type"], "parent")

    def test_nanny_cannot_start(self):
        res = self.nanny_client.post(
            "/api/v1/chat/conversations/start/",
            {"nanny_id": self.nanny_profile.id},
            format="json",
        )
        self.assertEqual(res.status_code, 403)

    def test_idor_messages_404(self):
        conv = self._start()
        res = self.other_client.get(f"/api/v1/chat/conversations/{conv['id']}/messages/")
        self.assertEqual(res.status_code, 404)

    def test_send_text_and_mark_read(self):
        conv = self._start()
        res = self.parent_client.post(
            f"/api/v1/chat/conversations/{conv['id']}/messages/",
            {"text": "Привіт"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["text"], "Привіт")
        self.assertTrue(res.json()["is_own"])

        listed = self.nanny_client.get(f"/api/v1/chat/conversations/{conv['id']}/messages/")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()["results"]), 1)
        self.assertFalse(listed.json()["results"][0]["is_own"])

        inbox = self.nanny_client.get("/api/v1/chat/conversations/")
        item = next(c for c in inbox.json()["results"] if c["id"] == conv["id"])
        self.assertEqual(item["unread_count"], 0)

    def test_messages_latest_and_before_id(self):
        conv = self._start()
        for i in range(55):
            Message.objects.create(
                conversation_id=conv["id"],
                sender=self.parent_user,
                text=f"m{i}",
            )
        page = self.parent_client.get(f"/api/v1/chat/conversations/{conv['id']}/messages/")
        self.assertEqual(page.status_code, 200)
        body = page.json()
        self.assertEqual(len(body["results"]), 50)
        self.assertTrue(body["has_more"])
        self.assertEqual(body["results"][-1]["text"], "m54")

        oldest_in_page = body["results"][0]["id"]
        older = self.parent_client.get(
            f"/api/v1/chat/conversations/{conv['id']}/messages/?before_id={oldest_in_page}"
        )
        self.assertEqual(older.status_code, 200)
        self.assertEqual(len(older.json()["results"]), 5)
        self.assertFalse(older.json()["has_more"])

    def test_send_photo_and_attachment_endpoint(self):
        conv = self._start()
        photo = SimpleUploadedFile("test.jpg", b"fake-image-bytes", content_type="image/jpeg")
        res = self.parent_client.post(
            f"/api/v1/chat/conversations/{conv['id']}/messages/",
            {"attachment": photo},
            format="multipart",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["attachment_type"], "photo")
        url = res.json()["attachment"]
        self.assertIn("/api/v1/chat/messages/", url)
        self.assertIn("t=", url)

        msg_id = res.json()["id"]
        att = self.parent_client.get(f"/api/v1/chat/messages/{msg_id}/attachment/")
        self.assertEqual(att.status_code, 200)

        denied = self.other_client.get(f"/api/v1/chat/messages/{msg_id}/attachment/")
        self.assertEqual(denied.status_code, 404)

        # signed token works without auth
        anon = APIClient()
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        token = qs["t"][0]
        ok = anon.get(f"/api/v1/chat/messages/{msg_id}/attachment/?t={token}")
        self.assertEqual(ok.status_code, 200)

    def test_reject_empty_message(self):
        conv = self._start()
        res = self.parent_client.post(
            f"/api/v1/chat/conversations/{conv['id']}/messages/",
            {},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_blocked_cannot_send(self):
        conv = self._start()
        self.parent_user.status = User.Status.BLOCKED
        self.parent_user.save(update_fields=["status"])
        res = self.parent_client.post(
            f"/api/v1/chat/conversations/{conv['id']}/messages/",
            {"text": "nope"},
            format="json",
        )
        self.assertEqual(res.status_code, 403)

    def test_media_chat_path_denied(self):
        conv = self._start()
        photo = SimpleUploadedFile("deny.jpg", b"abc", content_type="image/jpeg")
        res = self.parent_client.post(
            f"/api/v1/chat/conversations/{conv['id']}/messages/",
            {"attachment": photo},
            format="multipart",
        )
        self.assertEqual(res.status_code, 201)
        msg = Message.objects.get(pk=res.json()["id"])
        direct = self.parent_client.get(msg.attachment.url)
        self.assertEqual(direct.status_code, 404)


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
    ALLOWED_HOSTS=["localhost", "testserver", "127.0.0.1"],
)
class MessagingWebsocketTest(TransactionTestCase):
    def setUp(self):
        self.city = City.objects.create(name="Львів", slug="lviv")
        self.parent_user = User.objects.create_user(
            username="ws_parent",
            email="ws_parent@test.ua",
            password="SecurePass123!",
            role=User.Role.PARENT,
            status=User.Status.ACTIVE,
        )
        ParentProfile.objects.create(user=self.parent_user, first_name="WS")
        self.nanny_user = User.objects.create_user(
            username="ws_nanny",
            email="ws_nanny@test.ua",
            password="SecurePass123!",
            role=User.Role.NANNY,
            status=User.Status.ACTIVE,
        )
        self.nanny = NannyProfile.objects.create(
            user=self.nanny_user,
            first_name="WSN",
            city=self.city,
            moderation_status=NannyProfile.ModerationStatus.APPROVED,
            is_verified=True,
        )
        self.conv = Conversation.objects.create(
            parent=self.parent_user.parent_profile,
            nanny=self.nanny,
        )

    def _access_token(self, email):
        client = APIClient()
        res = client.post(
            "/api/v1/auth/login/",
            {"email": email, "password": "SecurePass123!"},
            format="json",
        )
        return res.json()["tokens"]["access"]

    def test_ws_auth_message(self):
        from asgiref.sync import async_to_sync
        from channels.testing import WebsocketCommunicator

        from config.asgi import application

        token = self._access_token("ws_parent@test.ua")

        async def _run():
            communicator = WebsocketCommunicator(
                application,
                f"/ws/chat/{self.conv.id}/",
                headers=[(b"origin", b"http://localhost")],
            )
            connected, _ = await communicator.connect()
            assert connected
            await communicator.send_json_to({"type": "auth", "token": token})
            response = await communicator.receive_json_from()
            assert response["type"] == "auth_ok"
            await communicator.disconnect()

        async_to_sync(_run)()

    def test_ws_rejects_bad_token(self):
        from asgiref.sync import async_to_sync
        from channels.testing import WebsocketCommunicator

        from config.asgi import application

        async def _run():
            communicator = WebsocketCommunicator(
                application,
                f"/ws/chat/{self.conv.id}/",
                headers=[(b"origin", b"http://localhost")],
            )
            connected, _ = await communicator.connect()
            assert connected
            await communicator.send_json_to({"type": "auth", "token": "bad"})
            # Server closes with 4001; communicator surfaces disconnect
            event = await communicator.receive_output(timeout=2)
            assert event["type"] in ("websocket.close", "websocket.disconnect")
            await communicator.disconnect()

        async_to_sync(_run)()