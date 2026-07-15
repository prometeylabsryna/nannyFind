from rest_framework import generics

from apps.accounts.permissions import IsParent
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewCreateSerializer, ReviewPublicSerializer


class ReviewCreateView(generics.CreateAPIView):
    permission_classes = [IsParent]
    serializer_class = ReviewCreateSerializer

    def perform_create(self, serializer):
        serializer.save(parent=self.request.user.parent_profile)


class NannyReviewsView(generics.ListAPIView):
    serializer_class = ReviewPublicSerializer

    def get_queryset(self):
        return Review.objects.filter(
            nanny_id=self.kwargs["nanny_id"],
            is_published=True,
        )
