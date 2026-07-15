from django.urls import path

from apps.reviews.views import NannyReviewsView, ReviewCreateView

urlpatterns = [
    path("", ReviewCreateView.as_view(), name="review-create"),
    path("nanny/<int:nanny_id>/", NannyReviewsView.as_view(), name="review-list"),
]
