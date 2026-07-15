from decouple import Csv, config

from .base import *  # noqa: F403

DEBUG = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SAMESITE = "Strict"

# Листи шле apps.core.email_service через Resend (RESEND_API_KEY, DEFAULT_FROM_EMAIL — у base.py).
SERVER_EMAIL = config("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)  # noqa: F405

LOGGING["root"]["level"] = config("LOG_LEVEL", default="WARNING")  # noqa: F405
