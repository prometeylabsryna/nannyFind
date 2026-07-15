from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from apps.core.views import HealthView
from apps.messaging.views import deny_chat_media

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("healthz/", HealthView.as_view(), name="healthz"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/nannies/", include("apps.nannies.urls")),
    path("api/v1/parents/", include("apps.parents.urls")),
    path("api/v1/chat/", include("apps.messaging.urls")),
    path("api/v1/payments/", include("apps.payments.urls")),
    path("api/v1/reviews/", include("apps.reviews.urls")),
    path("api/v1/content/", include("apps.content.urls")),
    path("api/v1/geo/", include("apps.geo.urls")),
    path("api/v1/", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("media/<path:path>", deny_chat_media),
    ]
