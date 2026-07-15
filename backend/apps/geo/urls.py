from django.urls import path

from apps.geo.views import CityListView

urlpatterns = [
    path("cities/", CityListView.as_view(), name="city-list"),
]
