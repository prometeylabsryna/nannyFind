from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.parents.models import ContactUnlock, Favorite, ParentProfile


@admin.register(ParentProfile)
class ParentProfileAdmin(ModelAdmin):
    list_display = ("last_name", "first_name", "city", "user")
    search_fields = ("first_name", "last_name", "user__email", "city")
    autocomplete_fields = ("user",)


@admin.register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ("parent", "nanny", "created_at")
    search_fields = ("parent__user__email", "nanny__first_name", "nanny__last_name")
    autocomplete_fields = ("parent", "nanny")


@admin.register(ContactUnlock)
class ContactUnlockAdmin(ModelAdmin):
    list_display = ("parent", "nanny", "unlocked_at")
    search_fields = ("parent__user__email", "nanny__first_name")
    autocomplete_fields = ("parent", "nanny")
