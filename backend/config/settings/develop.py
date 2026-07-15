from decouple import config

from .base import *  # noqa: F403

DEBUG = True
SECRET_KEY = config("SECRET_KEY", default="dev-only-insecure-key-do-not-use-in-prod")

INSTALLED_APPS += ["whitenoise.runserver_nostatic"]  # noqa: F405

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
