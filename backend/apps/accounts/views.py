from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.oauth import (
    OAuthNotConfigured,
    OAuthVerificationError,
    get_or_create_oauth_user,
    verify_oauth_token,
)
from apps.accounts.serializers import (
    OAuthLoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"user": UserSerializer(user).data, "tokens": _tokens_for_user(user)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").lower().strip()
        password = request.data.get("password") or ""
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"detail": "Невірний email або пароль."}, status=400)
        if user.status == User.Status.BLOCKED:
            return Response({"detail": "Акаунт заблоковано."}, status=403)
        if not user.check_password(password):
            return Response({"detail": "Невірний email або пароль."}, status=400)
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return Response({"user": UserSerializer(user).data, "tokens": _tokens_for_user(user)})


class OAuthLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OAuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.validated_data["provider"]
        try:
            profile = verify_oauth_token(
                provider,
                serializer.validated_data.get("access_token", ""),
                serializer.validated_data.get("id_token", ""),
            )
            user = get_or_create_oauth_user(provider, profile, serializer.validated_data["role"])
        except OAuthNotConfigured as exc:
            return Response({"detail": str(exc), "configured": False}, status=503)
        except OAuthVerificationError as exc:
            return Response({"detail": str(exc)}, status=400)
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return Response({"user": UserSerializer(user).data, "tokens": _tokens_for_user(user)})


class OAuthStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from django.conf import settings

        return Response(
            {
                "google": bool(settings.OAUTH_GOOGLE_CLIENT_ID),
                "google_client_id": settings.OAUTH_GOOGLE_CLIENT_ID or "",
                "facebook": bool(settings.OAUTH_FACEBOOK_APP_ID),
                "facebook_app_id": settings.OAUTH_FACEBOOK_APP_ID or "",
                "apple": bool(settings.OAUTH_APPLE_CLIENT_ID),
                "apple_client_id": settings.OAUTH_APPLE_CLIENT_ID or "",
            }
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        user = User.objects.filter(email__iexact=email).first()
        if user:
            from django.conf import settings

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = (
                f"{settings.FRONTEND_URL.rstrip('/')}/reset-password"
                f"?uid={uid}&token={token}"
            )
            send_mail(
                "Скидання пароля — Поміч поруч",
                f"Посилання для скидання: {reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        return Response({"detail": "Якщо email існує, лист надіслано."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Невалідне посилання."}, status=400)
        if not default_token_generator.check_token(user, serializer.validated_data["token"]):
            return Response({"detail": "Токен прострочено."}, status=400)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Пароль оновлено."})
