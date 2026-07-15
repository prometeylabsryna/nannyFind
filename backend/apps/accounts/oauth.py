import logging

import requests
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class OAuthNotConfigured(Exception):
    pass


class OAuthVerificationError(Exception):
    pass


def _provider_configured(provider: str) -> bool:
    mapping = {
        "google": (settings.OAUTH_GOOGLE_CLIENT_ID, settings.OAUTH_GOOGLE_CLIENT_SECRET),
        "facebook": (settings.OAUTH_FACEBOOK_APP_ID, settings.OAUTH_FACEBOOK_APP_SECRET),
        "apple": (settings.OAUTH_APPLE_CLIENT_ID, settings.OAUTH_APPLE_TEAM_ID),
    }
    return all(mapping.get(provider, ("", "")))


def verify_oauth_token(provider: str, access_token: str = "", id_token: str = "") -> dict:
    if not _provider_configured(provider):
        raise OAuthNotConfigured(f"OAuth {provider} не налаштовано. Додайте ключі в .env.")

    if provider == "google":
        if id_token:
            resp = requests.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": id_token},
                timeout=10,
            )
            if resp.status_code != 200:
                raise OAuthVerificationError("Невалідний Google token.")
            data = resp.json()
            if settings.OAUTH_GOOGLE_CLIENT_ID and data.get("aud") != settings.OAUTH_GOOGLE_CLIENT_ID:
                raise OAuthVerificationError("Невалідний Google client.")
            return {
                "email": data.get("email", "").lower(),
                "uid": data.get("sub", ""),
                "first_name": data.get("given_name", ""),
                "last_name": data.get("family_name", ""),
            }
        if not access_token:
            raise OAuthVerificationError("Потрібен access_token або id_token.")
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if resp.status_code != 200:
            raise OAuthVerificationError("Невалідний Google token.")
        data = resp.json()
        return {
            "email": data.get("email", "").lower(),
            "uid": data.get("sub", ""),
            "first_name": data.get("given_name", ""),
            "last_name": data.get("family_name", ""),
        }

    if provider == "facebook":
        resp = requests.get(
            "https://graph.facebook.com/me",
            params={
                "fields": "id,email,first_name,last_name",
                "access_token": access_token,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            raise OAuthVerificationError("Невалідний Facebook token.")
        data = resp.json()
        return {
            "email": (data.get("email") or f"{data['id']}@facebook.oauth").lower(),
            "uid": data.get("id", ""),
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
        }

    if provider == "apple":
        if not id_token:
            raise OAuthVerificationError("Потрібен Apple id_token.")
        try:
            import jwt
            from jwt import PyJWKClient
        except ImportError as exc:
            raise OAuthNotConfigured("Встановіть PyJWT для Apple Sign In.") from exc

        jwks_client = PyJWKClient("https://appleid.apple.com/auth/keys", cache_keys=True)
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        data = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.OAUTH_APPLE_CLIENT_ID,
        )
        email = (data.get("email") or f"{data.get('sub', '')}@privaterelay.appleid.com").lower()
        return {
            "email": email,
            "uid": data.get("sub", ""),
            "first_name": "",
            "last_name": "",
        }

    raise OAuthVerificationError("Невідомий провайдер.")


def get_or_create_oauth_user(provider: str, profile: dict, role: str) -> User:
    uid = profile["uid"]
    email = profile["email"]
    user = User.objects.filter(oauth_provider=provider, oauth_uid=uid).first()
    if user:
        return user

    user = User.objects.filter(email__iexact=email).first()
    if user:
        user.oauth_provider = provider
        user.oauth_uid = uid
        user.status = User.Status.ACTIVE
        user.save(update_fields=["oauth_provider", "oauth_uid", "status"])
        return user

    user = User.objects.create_user(
        username=email.split("@")[0][:150],
        email=email,
        password=User.objects.make_random_password(length=32),
        role=role,
        status=User.Status.ACTIVE,
        first_name=profile.get("first_name", ""),
        last_name=profile.get("last_name", ""),
        oauth_provider=provider,
        oauth_uid=uid,
    )
    if role == User.Role.PARENT:
        from apps.parents.models import ParentProfile

        ParentProfile.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
        )
    elif role == User.Role.NANNY:
        from apps.geo.models import City
        from apps.nannies.models import NannyProfile

        city = City.objects.first()
        if city:
            NannyProfile.objects.create(
                user=user,
                first_name=user.first_name or user.username,
                last_name=user.last_name,
                city=city,
            )
    return user
