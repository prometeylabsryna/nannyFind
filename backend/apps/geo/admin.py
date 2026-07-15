from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.geo.models import City, District


class DistrictInline(TabularInline):
    model = District
    extra = 0
    fields = ("name", "slug")


@admin.register(City)
class CityAdmin(ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    inlines = [DistrictInline]


@admin.register(District)
class DistrictAdmin(ModelAdmin):
    list_display = ("name", "city", "slug")
    list_filter = ("city",)
    list_filter_submit = True
    search_fields = ("name", "city__name")
    autocomplete_fields = ("city",)
