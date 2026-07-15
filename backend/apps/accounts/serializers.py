from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_platform_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "username", "phone", "role", "status", "is_platform_admin")
        read_only_fields = fields

    def get_is_platform_admin(self, obj):
        return obj.is_platform_admin


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=12, write_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices)
    first_name = serializers.CharField(max_length=64, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=64, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email вже зареєстровано.")
        return value.lower()

    def create(self, validated_data):
        role = validated_data.pop("role")
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        user_status = User.Status.PENDING if role == User.Role.NANNY else User.Status.ACTIVE
        user = User.objects.create_user(
            username=validated_data["email"].split("@")[0],
            email=validated_data["email"],
            password=validated_data["password"],
            role=role,
            status=user_status,
            first_name=first_name,
            last_name=last_name,
        )
        if role == User.Role.PARENT:
            from apps.parents.models import ParentProfile

            ParentProfile.objects.create(user=user, first_name=first_name, last_name=last_name)
        elif role == User.Role.NANNY:
            from apps.geo.models import City
            from apps.nannies.models import NannyProfile

            city = City.objects.first()
            if city:
                NannyProfile.objects.create(
                    user=user,
                    first_name=first_name or user.username,
                    last_name=last_name,
                    city=city,
                )
        return user


class OAuthLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=("google", "facebook", "apple"))
    access_token = serializers.CharField(required=False, allow_blank=True, default="")
    id_token = serializers.CharField(required=False, allow_blank=True, default="")
    role = serializers.ChoiceField(
        choices=User.Role.choices,
        required=False,
        default=User.Role.PARENT,
    )

    def validate(self, attrs):
        if attrs["provider"] == "google" and not attrs.get("access_token") and not attrs.get("id_token"):
            raise serializers.ValidationError("Потрібен access_token або id_token для Google.")
        if attrs["provider"] != "google" and not attrs.get("access_token"):
            raise serializers.ValidationError("Потрібен access_token.")
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=12, write_only=True)
