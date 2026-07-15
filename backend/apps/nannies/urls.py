from django.urls import path

from apps.nannies.views import (
    MyNannyProfileView,
    NannyAvailabilityView,
    NannyDetailView,
    NannyDocumentListView,
    NannyListView,
)

urlpatterns = [
    path("", NannyListView.as_view(), name="nanny-list"),
    path("me/", MyNannyProfileView.as_view(), name="nanny-me"),
    path("me/availability/", NannyAvailabilityView.as_view(), name="nanny-availability"),
    path("me/documents/", NannyDocumentListView.as_view(), name="nanny-documents"),
    path("<int:pk>/", NannyDetailView.as_view(), name="nanny-detail"),
]
