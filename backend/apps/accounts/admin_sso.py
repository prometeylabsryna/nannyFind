import secrets
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsPlatformAdmin

User = get_user_model()

SSO_CACHE_PREFIX = "admin_sso:"
SSO_TTL_SECONDS = 120


def _safe_admin_next(raw: str) -> str:
    path = str(raw or "/admin/").strip()
    if not path.startswith("/admin"):
        return "/admin/"
    if path.startswith("//") or "://" in path:
        return "/admin/"
    return path


def _can_use_django_admin(user) -> bool:
    return bool(
        user.is_authenticated
        and user.is_active
        and (user.is_staff or user.is_superuser or user.role == User.Role.ADMIN)
    )


class AdminBridgeView(APIView):
    """Створює одноразове посилання для входу в Django admin з JWT-сесії сайту."""

    permission_classes = [IsPlatformAdmin]

    def post(self, request):
        if not _can_use_django_admin(request.user):
            return Response({"detail": "Немає доступу до Django admin."}, status=403)

        next_url = _safe_admin_next(request.data.get("next"))
        code = secrets.token_urlsafe(32)
        cache.set(f"{SSO_CACHE_PREFIX}{code}", request.user.pk, timeout=SSO_TTL_SECONDS)

        base = settings.BACKEND_URL.rstrip("/")
        url = f"{base}/api/v1/auth/admin-enter/?code={quote(code)}&next={quote(next_url)}"
        return Response({"url": url})


class AdminEnterView(View):
    """Обмінює одноразовий код на Django session і редіректить в /admin/."""

    def get(self, request):
        code = request.GET.get("code", "")
        next_url = _safe_admin_next(request.GET.get("next"))
        user_id = cache.get(f"{SSO_CACHE_PREFIX}{code}")
        if not user_id:
            return redirect(f"/admin/login/?next={quote(next_url)}")

        cache.delete(f"{SSO_CACHE_PREFIX}{code}")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return redirect("/admin/login/")

        if not _can_use_django_admin(user):
            return redirect("/admin/login/")

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return HttpResponseRedirect(next_url)
