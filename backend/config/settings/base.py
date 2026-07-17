from datetime import timedelta
from pathlib import Path

from decouple import Csv, config
from django.templatetags.static import static
from django.urls import reverse_lazy

from apps.core.site_content_registry import build_content_sidebar_navigation_groups

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "daphne",
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_filters",
    "rest_framework",
    "rest_framework_simplejwt",
    "tinymce",
    "apps.accounts",
    "apps.geo",
    "apps.nannies",
    "apps.parents",
    "apps.messaging",
    "apps.payments",
    "apps.reviews",
    "apps.content",
    "apps.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="pomich_poruch"),
        "USER": config("DB_USER", default="pomich"),
        "PASSWORD": config("DB_PASSWORD", default="pomich"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uk"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticatedOrReadOnly",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_RATES": {
        "chat_message": "60/min",
    },
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
}

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default=(
        "http://localhost:8080,http://127.0.0.1:8080,"
        "http://localhost:8082,http://127.0.0.1:8082,"
        "http://localhost:8081,http://127.0.0.1:8081"
    ),
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default=(
        "http://localhost:8080,http://127.0.0.1:8080,"
        "http://localhost:8082,http://127.0.0.1:8082,"
        "http://localhost:8081,http://127.0.0.1:8081"
    ),
    cast=Csv(),
)

_redis_url = config("REDIS_URL", default="")
if _redis_url:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                # redis-py >=8.0 дефолтить socket_timeout=5s, а channels_redis
                # чекає на блокуючий BRPOP/BZPOPMIN із тим самим 5s server-side
                # timeout — клієнт зрідка встигає кинути TimeoutError раніше,
                # ніж сервер штатно повертає "нема повідомлень" (WS рветься
                # без причини). socket_timeout=None вимикає client-side read
                # timeout саме для цього з'єднання. Див. django/channels_redis#422.
                "hosts": [{"address": _redis_url, "socket_timeout": None}],
            },
        }
    }
else:
    CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:8082")
_backend_url = config("BACKEND_URL", default="")
if _backend_url:
    BACKEND_URL = _backend_url.rstrip("/")
else:
    BACKEND_URL = (
        FRONTEND_URL.replace(":8082", ":8001")
        .replace(":8080", ":8000")
        .rstrip("/")
    )

OAUTH_GOOGLE_CLIENT_ID = config("OAUTH_GOOGLE_CLIENT_ID", default="")
OAUTH_GOOGLE_CLIENT_SECRET = config("OAUTH_GOOGLE_CLIENT_SECRET", default="")
OAUTH_FACEBOOK_APP_ID = config("OAUTH_FACEBOOK_APP_ID", default="")
OAUTH_FACEBOOK_APP_SECRET = config("OAUTH_FACEBOOK_APP_SECRET", default="")
OAUTH_APPLE_CLIENT_ID = config("OAUTH_APPLE_CLIENT_ID", default="")
OAUTH_APPLE_TEAM_ID = config("OAUTH_APPLE_TEAM_ID", default="")
OAUTH_APPLE_KEY_ID = config("OAUTH_APPLE_KEY_ID", default="")
OAUTH_APPLE_PRIVATE_KEY = config("OAUTH_APPLE_PRIVATE_KEY", default="")

PLATFORM_COMMISSION_RATE = config("PLATFORM_COMMISSION_RATE", default=0.1, cast=float)

LIQPAY_PUBLIC_KEY = config("LIQPAY_PUBLIC_KEY", default="")
LIQPAY_PRIVATE_KEY = config("LIQPAY_PRIVATE_KEY", default="")
WAYFORPAY_MERCHANT_ACCOUNT = config("WAYFORPAY_MERCHANT_ACCOUNT", default="")
WAYFORPAY_SECRET_KEY = config("WAYFORPAY_SECRET_KEY", default="")
FONDY_MERCHANT_ID = config("FONDY_MERCHANT_ID", default="")
FONDY_SECRET_KEY = config("FONDY_SECRET_KEY", default="")

_payments_stub_raw = config("PAYMENTS_STUB_MODE", default="auto")
if _payments_stub_raw == "auto":
    PAYMENTS_STUB_MODE = not any(
        [LIQPAY_PUBLIC_KEY, WAYFORPAY_MERCHANT_ACCOUNT, FONDY_MERCHANT_ID]
    )
else:
    PAYMENTS_STUB_MODE = _payments_stub_raw.lower() in ("1", "true", "yes")

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@pomich-poruch.com.ua")
RESEND_API_KEY = config("RESEND_API_KEY", default="")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

UNFOLD = {
    "SITE_TITLE": "Поміч поруч",
    "SITE_HEADER": "Поміч поруч — Адмінпанель",
    "SITE_SYMBOL": "child_care",
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "any",
            "type": "image/x-icon",
            "href": lambda request: static("favicons/favicon.ico"),
        },
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("favicons/favicon-32x32.png"),
        },
        {
            "rel": "icon",
            "sizes": "16x16",
            "type": "image/png",
            "href": lambda request: static("favicons/favicon-16x16.png"),
        },
        {
            "rel": "apple-touch-icon",
            "sizes": "180x180",
            "type": "image/png",
            "href": lambda request: static("favicons/apple-touch-icon.png"),
        },
    ],
    "SIDEBAR": {
        "show_search": True,
        "command_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Налаштування",
                "items": [
                    {
                        "title": "Сайт",
                        "icon": "settings",
                        "link": reverse_lazy("admin:core_sitesettings_changelist"),
                    },
                ],
            },
            *build_content_sidebar_navigation_groups(),
            {
                "title": "Контент",
                "separator": True,
                "items": [
                    {
                        "title": "📄 Статичні сторінки",
                        "icon": "web",
                        "link": reverse_lazy("admin:content_staticpage_changelist"),
                    },
                    {
                        "title": "❓ FAQ",
                        "icon": "help",
                        "link": reverse_lazy("admin:content_faqitem_changelist"),
                    },
                    {
                        "title": "📰 Блог",
                        "icon": "newspaper",
                        "link": reverse_lazy("admin:content_blogpost_changelist"),
                    },
                ],
            },
            {
                "title": "Модерація",
                "separator": True,
                "items": [
                    {
                        "title": "Профілі нянь",
                        "icon": "badge",
                        "link": reverse_lazy("admin:nannies_nannyprofile_changelist"),
                    },
                    {
                        "title": "Документи",
                        "icon": "description",
                        "link": reverse_lazy("admin:nannies_nannydocument_changelist"),
                    },
                    {
                        "title": "Відгуки",
                        "icon": "rate_review",
                        "link": reverse_lazy("admin:reviews_review_changelist"),
                    },
                ],
            },
            {
                "title": "Користувачі",
                "separator": True,
                "items": [
                    {
                        "title": "Акаунти",
                        "icon": "group",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                    },
                    {
                        "title": "Батьки",
                        "icon": "family_restroom",
                        "link": reverse_lazy("admin:parents_parentprofile_changelist"),
                    },
                ],
            },
            {
                "title": "Географія",
                "separator": True,
                "items": [
                    {
                        "title": "Міста",
                        "icon": "location_city",
                        "link": reverse_lazy("admin:geo_city_changelist"),
                    },
                ],
            },
            {
                "title": "Фінанси",
                "separator": True,
                "items": [
                    {
                        "title": "Платежі",
                        "icon": "payments",
                        "link": reverse_lazy("admin:payments_payment_changelist"),
                    },
                    {
                        "title": "Тарифи",
                        "icon": "sell",
                        "link": reverse_lazy("admin:payments_pricingplan_changelist"),
                    },
                    {
                        "title": "Підписки",
                        "icon": "card_membership",
                        "link": reverse_lazy("admin:payments_subscription_changelist"),
                    },
                ],
            },
            {
                "title": "Комунікації",
                "separator": True,
                "items": [
                    {
                        "title": "Чати",
                        "icon": "forum",
                        "link": reverse_lazy("admin:messaging_conversation_changelist"),
                    },
                ],
            },
        ],
    },
}

TINYMCE_DEFAULT_CONFIG = {
    "height": 400,
    "menubar": False,
    "plugins": "link lists image code",
    "toolbar": "undo redo | bold italic underline | bullist numlist | link image | code",
    "content_css": False,
    "skin": "oxide",
}

CONTENT_SECURITY_POLICY = {
    "EXCLUDE_URL_PREFIXES": ("/admin/",),
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'", "https://secure.wayforpay.com", "https://unpkg.com"),
        "style-src": ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com"),
        "img-src": ("'self'", "data:", "https:"),
        "form-action": (
            "'self'",
            "https://www.liqpay.ua",
            "https://secure.wayforpay.com",
            "https://pay.fondy.eu",
        ),
        "connect-src": ("'self'", "https://api.fondy.eu", "ws:", "wss:"),
    }
}
