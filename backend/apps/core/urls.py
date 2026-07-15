from django.urls import path

from apps.core.content_api import SiteBlocksView
from apps.core.views import (
    AdminAnalyticsView,
    AdminDashboardView,
    AdminDocumentsView,
    AdminPaymentsView,
    AdminProfileModerationView,
    AdminUserListView,
)

urlpatterns = [
    path("content/blocks/", SiteBlocksView.as_view(), name="site-blocks"),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("admin/users/", AdminUserListView.as_view(), name="admin-users"),
    path("admin/profiles/", AdminProfileModerationView.as_view(), name="admin-profiles"),
    path("admin/documents/", AdminDocumentsView.as_view(), name="admin-documents"),
    path("admin/payments/", AdminPaymentsView.as_view(), name="admin-payments"),
    path("admin/analytics/", AdminAnalyticsView.as_view(), name="admin-analytics"),
]
