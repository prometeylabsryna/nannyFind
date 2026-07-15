from django.urls import path

from apps.parents.views import FavoriteDeleteView, FavoriteListView, ParentProfileView, ReviewableNanniesView

urlpatterns = [
    path("profile/", ParentProfileView.as_view(), name="parent-profile"),
    path("favorites/", FavoriteListView.as_view(), name="parent-favorites"),
    path("favorites/<int:nanny_id>/", FavoriteDeleteView.as_view(), name="parent-favorite-delete"),
    path("reviewable/", ReviewableNanniesView.as_view(), name="parent-reviewable"),
]
