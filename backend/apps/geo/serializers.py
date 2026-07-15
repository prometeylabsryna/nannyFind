from rest_framework import serializers

from apps.geo.models import City, District


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("name", "slug")


class CitySerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ("name", "slug", "districts")
