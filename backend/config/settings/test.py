from .base import *  # noqa: F403

SECRET_KEY = "test-secret-key-not-for-production"
DEBUG = False

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
ALLOWED_HOSTS = ["localhost", "testserver", "127.0.0.1"]

