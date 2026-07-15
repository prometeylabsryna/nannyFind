from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.admin_sso import AdminBridgeView, AdminEnterView
from apps.accounts.views import (
    LoginView,
    MeView,
    OAuthLoginView,
    OAuthStatusView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("oauth/", OAuthLoginView.as_view(), name="auth-oauth"),
    path("oauth/status/", OAuthStatusView.as_view(), name="auth-oauth-status"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("admin-bridge/", AdminBridgeView.as_view(), name="auth-admin-bridge"),
    path("admin-enter/", AdminEnterView.as_view(), name="auth-admin-enter"),
    path("password/reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]
