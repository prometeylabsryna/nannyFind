import django_filters
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsNanny
from apps.nannies.models import AvailabilitySlot, NannyDocument, NannyProfile
from apps.nannies.serializers import (
    AvailabilitySlotSerializer,
    NannyDetailSerializer,
    NannyDocumentSerializer,
    NannyListSerializer,
    NannyProfileUpdateSerializer,
)


class NannyFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name="city__name")
    district = django_filters.CharFilter(field_name="district__name")
    nannyAgeMin = django_filters.NumberFilter(method="filter_age_min")
    experienceMin = django_filters.NumberFilter(field_name="experience_years", lookup_expr="gte")
    hourlyRateMax = django_filters.NumberFilter(field_name="hourly_rate", lookup_expr="lte")
    ratingMin = django_filters.NumberFilter(field_name="rating_avg", lookup_expr="gte")
    hasCar = django_filters.BooleanFilter(field_name="has_car")
    medicalEducation = django_filters.BooleanFilter(field_name="medical_education")
    firstAidCourse = django_filters.BooleanFilter(field_name="first_aid_course")
    languages = django_filters.CharFilter(method="filter_languages")

    class Meta:
        model = NannyProfile
        fields = []

    def filter_age_min(self, queryset, name, value):
        from datetime import date

        cutoff = date.today().replace(year=date.today().year - int(value))
        return queryset.filter(birth_date__lte=cutoff)

    def filter_languages(self, queryset, name, value):
        langs = [x.strip() for x in value.split(",") if x.strip()]
        if not langs:
            return queryset
        q = Q()
        for lang in langs:
            q |= Q(languages__contains=[lang])
        return queryset.filter(q)


class NannyListView(generics.ListAPIView):
    serializer_class = NannyListSerializer
    filterset_class = NannyFilter
    search_fields = ["first_name", "last_name", "description"]
    ordering_fields = ["rating_avg", "hourly_rate", "experience_years"]

    def get_queryset(self):
        return (
            NannyProfile.objects.filter(
                moderation_status=NannyProfile.ModerationStatus.APPROVED,
                is_verified=True,
            )
            .select_related("city", "district", "user")
            .prefetch_related("availability")
        )


class NannyDetailView(generics.RetrieveAPIView):
    serializer_class = NannyDetailSerializer
    lookup_field = "pk"

    def get_queryset(self):
        base = NannyProfile.objects.select_related("city", "district", "user").prefetch_related(
            "availability", "reviews"
        )
        public = Q(
            moderation_status=NannyProfile.ModerationStatus.APPROVED,
            is_verified=True,
        )
        user = self.request.user
        if not user.is_authenticated:
            return base.filter(public)
        if user.role == User.Role.ADMIN or user.is_staff or user.is_superuser:
            return base
        if user.role == User.Role.NANNY:
            own = getattr(user, "nanny_profile", None)
            if own:
                return base.filter(Q(pk=own.pk) | public)
        return base.filter(public)


class MyNannyProfileView(APIView):
    permission_classes = [IsNanny]

    def get(self, request):
        profile = request.user.nanny_profile
        return Response(NannyDetailSerializer(profile, context={"request": request}).data)

    def patch(self, request):
        profile = request.user.nanny_profile
        serializer = NannyProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(moderation_status=NannyProfile.ModerationStatus.PENDING)
        return Response(NannyDetailSerializer(profile, context={"request": request}).data)


class NannyAvailabilityView(APIView):
    permission_classes = [IsNanny]

    def get(self, request):
        slots = request.user.nanny_profile.availability.all()
        return Response(AvailabilitySlotSerializer(slots, many=True).data)

    def put(self, request):
        profile = request.user.nanny_profile
        if not isinstance(request.data, list):
            return Response(
                {"detail": "Очікується масив слотів."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        valid_status = {choice.value for choice in AvailabilitySlot.Status}
        for item in request.data:
            raw_date = item.get("date")
            slot_status = item.get("status", AvailabilitySlot.Status.AVAILABLE)
            if not raw_date:
                continue
            if slot_status not in valid_status:
                return Response(
                    {"detail": f"Невідомий статус: {slot_status}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            AvailabilitySlot.objects.update_or_create(
                nanny=profile,
                date=raw_date,
                defaults={"status": slot_status},
            )
        slots = profile.availability.all()
        return Response(AvailabilitySlotSerializer(slots, many=True).data)


class NannyDocumentListView(generics.ListCreateAPIView):
    permission_classes = [IsNanny]
    serializer_class = NannyDocumentSerializer

    def get_queryset(self):
        return NannyDocument.objects.filter(nanny=self.request.user.nanny_profile)

    def perform_create(self, serializer):
        profile = self.request.user.nanny_profile
        doc_type = serializer.validated_data["doc_type"]
        defaults = {"file": serializer.validated_data["file"], "status": NannyDocument.DocStatus.PENDING}
        obj, _ = NannyDocument.objects.update_or_create(
            nanny=profile,
            doc_type=doc_type,
            defaults=defaults,
        )
        serializer.instance = obj
        profile.moderation_status = NannyProfile.ModerationStatus.PENDING
        profile.save(update_fields=["moderation_status"])
