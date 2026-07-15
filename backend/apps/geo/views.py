from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.geo.models import City
from apps.geo.serializers import CitySerializer


class CityListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CitySerializer
    pagination_class = None
    queryset = City.objects.filter(is_active=True).prefetch_related("districts")
