from rest_framework import serializers

from apps.core.validators import validate_ua_phone
from apps.nannies.serializers import NannyListSerializer
from apps.parents.models import Favorite, ParentProfile


class ParentProfileSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city.name", allow_null=True)
    photo = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = ParentProfile
        fields = (
            "first_name",
            "last_name",
            "birth_date",
            "city",
            "photo",
            "phone",
            "children_count",
            "children_ages",
            "special_needs",
        )

    def get_photo(self, obj):
        return obj.display_photo

    def get_phone(self, obj):
        return obj.user.phone or None


class ParentProfileUpdateSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=False, write_only=True)
    clear_photo = serializers.BooleanField(required=False, write_only=True, default=False)

    class Meta:
        model = ParentProfile
        fields = (
            "first_name",
            "last_name",
            "birth_date",
            "city_name",
            "photo",
            "clear_photo",
            "phone",
            "children_count",
            "children_ages",
            "special_needs",
        )

    def validate_phone(self, value):
        return validate_ua_phone(value)

    def update(self, instance, validated_data):
        city_name = validated_data.pop("city_name", None)
        phone = validated_data.pop("phone", None)
        clear_photo = validated_data.pop("clear_photo", False)
        if city_name:
            from apps.geo.models import City

            city = City.objects.filter(name=city_name).first()
            if city:
                instance.city = city
        if clear_photo:
            if instance.photo:
                instance.photo.delete(save=False)
            validated_data.pop("photo", None)
        profile = super().update(instance, validated_data)
        if clear_photo:
            profile.photo = ""
            profile.save(update_fields=["photo"])
        if phone is not None:
            profile.user.phone = phone
            profile.user.save(update_fields=["phone"])
        return profile

    def validate_photo(self, photo):
        allowed = ("image/jpeg", "image/png", "image/webp")
        if photo.content_type not in allowed and not photo.name.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        ):
            raise serializers.ValidationError("Дозволено лише JPEG, PNG або WebP.")
        if photo.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Максимальний розмір фото — 5 МБ.")
        return photo


class FavoriteSerializer(serializers.ModelSerializer):
    nanny = NannyListSerializer(read_only=True)
    nanny_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = ("id", "nanny", "nanny_id", "created_at")
        read_only_fields = ("id", "created_at", "nanny")
