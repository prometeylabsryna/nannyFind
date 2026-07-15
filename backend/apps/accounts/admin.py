from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("email", "role", "status", "is_staff", "date_joined")
    list_filter = ("role", "status", "is_staff")
    list_filter_submit = True
    search_fields = ("email", "username", "phone")
    ordering = ("-date_joined",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Поміч поруч", {"fields": ("phone", "role", "status", "oauth_provider", "oauth_uid")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "role", "status"),
            },
        ),
    )
