from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsParent
from apps.nannies.models import NannyProfile
from apps.nannies.serializers import NannyListSerializer
from apps.parents.models import ContactUnlock, Favorite
from apps.parents.serializers import FavoriteSerializer, ParentProfileSerializer, ParentProfileUpdateSerializer
from apps.reviews.models import Review


class ParentProfileView(APIView):
    permission_classes = [IsParent]

    def get(self, request):
        profile = request.user.parent_profile
        return Response(ParentProfileSerializer(profile, context={"request": request}).data)

    def patch(self, request):
        profile = request.user.parent_profile
        serializer = ParentProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ParentProfileSerializer(profile, context={"request": request}).data)


class FavoriteListView(generics.ListCreateAPIView):
    permission_classes = [IsParent]
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(parent=self.request.user.parent_profile).select_related(
            "nanny__city", "nanny__district"
        ).prefetch_related("nanny__availability")

    def create(self, request, *args, **kwargs):
        nanny_id = request.data.get("nanny_id")
        nanny = NannyProfile.objects.filter(pk=nanny_id).first()
        if not nanny:
            return Response({"detail": "Няню не знайдено."}, status=404)
        fav, created = Favorite.objects.get_or_create(
            parent=request.user.parent_profile,
            nanny=nanny,
        )
        return Response(
            FavoriteSerializer(fav).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class FavoriteDeleteView(APIView):
    permission_classes = [IsParent]

    def delete(self, request, nanny_id):
        deleted, _ = Favorite.objects.filter(
            parent=request.user.parent_profile,
            nanny_id=nanny_id,
        ).delete()
        if not deleted:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewableNanniesView(APIView):
    """Няні з відкритим контактом, для яких ще немає відгуку."""

    permission_classes = [IsParent]

    def get(self, request):
        parent = request.user.parent_profile
        reviewed_ids = Review.objects.filter(parent=parent).values_list("nanny_id", flat=True)
        unlocks = (
            ContactUnlock.objects.filter(parent=parent)
            .exclude(nanny_id__in=reviewed_ids)
            .select_related("nanny__city", "nanny__district", "nanny__user")
            .prefetch_related("nanny__availability")
        )
        nannies = [u.nanny for u in unlocks]
        return Response(NannyListSerializer(nannies, many=True).data)
