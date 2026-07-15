from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.geo.models import City
from apps.nannies.models import NannyProfile


class HealthAPITest(TestCase):
    def test_healthz(self):
        client = APIClient()
        res = client.get("/healthz/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")


class AuthAPITest(TestCase):
    def test_register_and_login(self):
        client = APIClient()
        res = client.post(
            "/api/v1/auth/register/",
            {
                "email": "parent@test.ua",
                "password": "SecurePass123!",
                "role": "parent",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        res = client.post(
            "/api/v1/auth/login/",
            {"email": "parent@test.ua", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.json()["tokens"])


class NannyVisibilityAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.city = City.objects.create(name="Київ", slug="kyiv")
        nanny_user = User.objects.create_user(
            username="pending_nanny",
            email="pending@demo.ua",
            password="SecurePass123!",
            role=User.Role.NANNY,
            status=User.Status.PENDING,
        )
        self.pending = NannyProfile.objects.create(
            user=nanny_user,
            first_name="Тест",
            last_name="Няня",
            city=self.city,
            moderation_status=NannyProfile.ModerationStatus.PENDING,
            is_verified=False,
        )

    def test_pending_profile_hidden_from_public(self):
        res = self.client.get(f"/api/v1/nannies/{self.pending.pk}/")
        self.assertEqual(res.status_code, 404)

    def test_pending_profile_visible_to_owner(self):
        self.client.force_authenticate(user=self.pending.user)
        res = self.client.get(f"/api/v1/nannies/{self.pending.pk}/")
        self.assertEqual(res.status_code, 200)
