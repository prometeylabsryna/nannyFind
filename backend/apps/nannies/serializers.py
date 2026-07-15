from datetime import date, timedelta

from rest_framework import serializers

from apps.geo.models import City, District
from apps.nannies.models import AvailabilitySlot, NannyDocument, NannyProfile
from apps.core.validators import validate_ua_phone


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("id", "name", "slug")


class CitySerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ("id", "name", "slug", "districts")


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilitySlot
        fields = ("date", "status")


class NannyListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk")
    name = serializers.SerializerMethodField()
    city = serializers.CharField(source="city.name")
    district = serializers.CharField(source="district.name", allow_null=True)
    photo = serializers.SerializerMethodField()
    rating = serializers.DecimalField(source="rating_avg", max_digits=3, decimal_places=2)
    reviewCount = serializers.IntegerField(source="review_count")
    hourlyRate = serializers.IntegerField(source="hourly_rate")
    experienceYears = serializers.IntegerField(source="experience_years")
    isVerified = serializers.BooleanField(source="is_verified")
    hasCar = serializers.BooleanField(source="has_car")
    medicalEducation = serializers.BooleanField(source="medical_education")
    firstAidCourse = serializers.BooleanField(source="first_aid_course")
    availability = serializers.SerializerMethodField()
    completedOrders = serializers.SerializerMethodField()

    class Meta:
        model = NannyProfile
        fields = (
            "id",
            "name",
            "age",
            "city",
            "district",
            "photo",
            "rating",
            "reviewCount",
            "hourlyRate",
            "experienceYears",
            "description",
            "certificates",
            "languages",
            "hasCar",
            "medicalEducation",
            "firstAidCourse",
            "availability",
            "isVerified",
            "completedOrders",
        )

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_photo(self, obj):
        return obj.display_photo

    def get_availability(self, obj):
        start = date.today()
        end = start + timedelta(days=13)
        return {
            s.date.isoformat(): s.status
            for s in obj.availability.filter(date__gte=start, date__lte=end)
        }

    def get_completedOrders(self, obj):
        return obj.contact_unlocks.count()


class NannyDetailSerializer(NannyListSerializer):
    phone = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    birth_date = serializers.DateField(required=False, allow_null=True)
    families_count = serializers.IntegerField(required=False)
    recommendations = serializers.CharField(required=False, allow_blank=True)

    class Meta(NannyListSerializer.Meta):
        fields = NannyListSerializer.Meta.fields + (
            "phone",
            "reviews",
            "birth_date",
            "families_count",
            "recommendations",
        )

    def get_phone(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        if getattr(request.user, "nanny_profile", None) == obj:
            return obj.user.phone or None
        from apps.parents.models import ContactUnlock

        parent = getattr(request.user, "parent_profile", None)
        if not parent:
            return None
        if ContactUnlock.objects.filter(parent=parent, nanny=obj).exists():
            return obj.user.phone
        return None

    def get_reviews(self, obj):
        from apps.reviews.serializers import ReviewPublicSerializer

        qs = obj.reviews.filter(is_published=True)[:20]
        return ReviewPublicSerializer(qs, many=True).data


class NannyProfileUpdateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=32, required=False, allow_blank=False, write_only=True)
    clear_photo = serializers.BooleanField(required=False, write_only=True, default=False)

    class Meta:
        model = NannyProfile
        fields = (
            "first_name",
            "last_name",
            "birth_date",
            "city",
            "district",
            "description",
            "hourly_rate",
            "experience_years",
            "families_count",
            "recommendations",
            "languages",
            "certificates",
            "has_car",
            "medical_education",
            "first_aid_course",
            "photo",
            "photo_url",
            "clear_photo",
            "phone",
        )

    def validate_phone(self, value):
        return validate_ua_phone(value)

    def update(self, instance, validated_data):
        phone = validated_data.pop("phone", None)
        clear_photo = validated_data.pop("clear_photo", False)
        if clear_photo:
            if instance.photo:
                instance.photo.delete(save=False)
            instance.photo = ""
            instance.photo_url = ""
            validated_data.pop("photo", None)
            validated_data["photo_url"] = ""
        profile = super().update(instance, validated_data)
        if clear_photo:
            profile.photo = ""
            profile.photo_url = ""
            profile.save(update_fields=["photo", "photo_url"])
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


class NannyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NannyDocument
        fields = ("id", "doc_type", "file", "status", "uploaded_at")
        read_only_fields = ("status", "uploaded_at")

    def validate_file(self, file):
        allowed = ("application/pdf", "image/jpeg", "image/png", "image/webp")
        if file.content_type not in allowed and not file.name.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
            raise serializers.ValidationError("Дозволено лише PDF або зображення.")
        if file.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Максимальний розмір файлу — 10 МБ.")
        return file
