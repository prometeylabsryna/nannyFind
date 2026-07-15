from rest_framework import serializers

from apps.reviews.models import Review


class ReviewPublicSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    rating = serializers.IntegerField()
    date = serializers.DateTimeField(source="created_at", format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Review
        fields = ("author", "rating", "text", "date")

    def get_author(self, obj):
        name = f"{obj.parent.last_name} {obj.parent.first_name[0]}.".strip()
        return name or "Батьки"


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("nanny", "rating", "text")

    def validate_nanny(self, nanny):
        parent = self.context["request"].user.parent_profile
        from apps.parents.models import ContactUnlock

        if not ContactUnlock.objects.filter(parent=parent, nanny=nanny).exists():
            raise serializers.ValidationError(
                "Відгук можна залишити лише після відкриття контакту та співпраці."
            )
        if Review.objects.filter(parent=parent, nanny=nanny).exists():
            raise serializers.ValidationError("Ви вже залишили відгук для цієї няні.")
        return nanny
