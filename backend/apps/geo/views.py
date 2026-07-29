from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.geo.models import City
from apps.geo.serializers import CitySerializer
from apps.nannies.catalog_coverage import cities_with_public_nannies


class CityListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CitySerializer
    pagination_class = None

    def get_queryset(self):
        if self.request.query_params.get("with_nannies") in {"1", "true", "True"}:
            return cities_with_public_nannies()
        return City.objects.filter(is_active=True).prefetch_related("districts")
