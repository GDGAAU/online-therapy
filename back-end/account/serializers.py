"""
account/serializers.py
=======================
Profile serializers used by custom profile endpoints and djoser user views.
"""

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer

from .models import Profile, CustomUser


class UserCreateSerializer(DjoserUserCreateSerializer):
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(write_only=True, required=False, allow_null=True)

    class Meta(DjoserUserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            "id",
            "email",
            "password",
            "re_password",
            "full_name",
            "phone_number",
            "date_of_birth",
        )

    def create(self, validated_data):
        full_name = validated_data.pop("full_name", "").strip()
        phone_number = validated_data.pop("phone_number", "")
        date_of_birth = validated_data.pop("date_of_birth", None)

        user = super().create(validated_data)
        profile, _ = Profile.objects.get_or_create(user=user)

        if full_name:
            parts = full_name.split()
            profile.first_name = parts[0]
            profile.last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        if phone_number:
            profile.phone_number = phone_number

        if date_of_birth:
            profile.date_of_birth = date_of_birth

        profile.save(update_fields=["first_name", "last_name", "phone_number", "date_of_birth"])
        return user


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "avatar_url",
            "bio",
            "phone_number",
            "date_of_birth",
        ]
        read_only_fields = ["id", "email"]

    def get_avatar_url(self, obj) -> str | None:
        if obj.avatar:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "bio", "phone_number", "date_of_birth", "avatar"]



class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()