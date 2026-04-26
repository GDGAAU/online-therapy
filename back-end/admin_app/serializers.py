from rest_framework import serializers
from django.db import transaction
from django.db.utils import IntegrityError
from account.models import CustomUser, Profile
from therapy.models import Therapist, Specialty, Appointment


class UserTypeField(serializers.SerializerMethodField):
    """Field that returns user_type based on is_staff and is_superuser."""

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        if value.is_superuser:
            return "admin"
        elif value.is_staff:
            return "therapist"
        else:
            return "patient"


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin user management."""
    user_type = UserTypeField(read_only=True)
    first_name = serializers.CharField(source="profile.first_name", read_only=True)
    last_name = serializers.CharField(source="profile.last_name", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "user_type",
            "is_active",
            "date_joined",
            "last_login",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id", "email", "user_type", "date_joined", "last_login"]


class UserAdminDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for user detail view with profile info."""
    user_type = UserTypeField(read_only=True)
    first_name = serializers.CharField(source="profile.first_name")
    last_name = serializers.CharField(source="profile.last_name")
    phone_number = serializers.CharField(source="profile.phone_number", read_only=True)
    avatar = serializers.ImageField(source="profile.avatar", read_only=True)
    bio = serializers.CharField(source="profile.bio", read_only=True)
    date_of_birth = serializers.DateField(source="profile.date_of_birth", read_only=True)
    profile_created_at = serializers.DateTimeField(source="profile.created_at", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "user_type",
            "is_active",
            "date_joined",
            "last_login",
            "first_name",
            "last_name",
            "phone_number",
            "avatar",
            "bio",
            "date_of_birth",
            "profile_created_at",
        ]
        read_only_fields = ["id", "email", "user_type", "date_joined", "last_login", "profile_created_at"]


class AdminTherapistCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    bio = serializers.CharField(allow_blank=True, required=False)
    specialties = serializers.ListField(child=serializers.UUIDField(), allow_empty=True, required=False)
    consultation_fee = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    license_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    years_of_experience = serializers.IntegerField(min_value=0, required=False, default=0)
    is_available = serializers.BooleanField(required=False, default=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def create(self, validated_data):
        specialties_ids = validated_data.pop("specialties", [])
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        bio = validated_data.pop("bio", "")
        consultation_fee = validated_data.pop("consultation_fee", None)
        license_number = validated_data.pop("license_number", "")
        years_of_experience = validated_data.pop("years_of_experience", 0)
        is_available = validated_data.pop("is_available", True)

        with transaction.atomic():
            # Create user without is_staff first to avoid signal creating therapist
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                is_staff=False,
                is_superuser=False,
                is_active=True,
            )
            profile, _ = Profile.objects.get_or_create(
                user=user
            )
            profile.first_name = first_name
            profile.last_name = last_name
            profile.save(update_fields=["first_name", "last_name"]) 

            # Create therapist profile
            therapist = Therapist.objects.create(
                user=user,
                bio=bio,
                consultation_fee=consultation_fee,
                license_number=license_number,
                years_of_experience=years_of_experience,
                is_available=is_available,
            )
            
            # Now update user to staff (signal won't create duplicate since therapist exists)
            user.is_staff = True
            user.save(update_fields=["is_staff"])

            if specialties_ids:
                specialties_qs = Specialty.objects.filter(id__in=specialties_ids)
                therapist.specialties.set(specialties_qs)

        return therapist


class AdminTherapistSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.profile.first_name", read_only=True)
    last_name = serializers.CharField(source="user.profile.last_name", read_only=True)
    specialties = serializers.SlugRelatedField(many=True, slug_field="name", read_only=True)

    class Meta:
        model = Therapist
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "bio",
            "specialties",
            "years_of_experience",
            "consultation_fee",
            "license_number",
            "is_available",
            "created_at",
            "updated_at",
        ]


# ─── Admin Appointment Serializers ────────────────────────────────────────────


class AdminAppointmentSerializer(serializers.ModelSerializer):
    """Read-only serializer for admin appointment list / detail."""

    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    patient_name = serializers.SerializerMethodField()
    therapist_name = serializers.SerializerMethodField()
    therapist_id = serializers.UUIDField(source="therapist.id", read_only=True)
    patient_id = serializers.UUIDField(source="patient.id", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient_id",
            "patient_email",
            "patient_name",
            "therapist_id",
            "therapist_name",
            "status",
            "appointment_type",
            "scheduled_at",
            "duration_minutes",
            "reason",
            "cancellation_reason",
            "meeting_link",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_patient_name(self, obj) -> str:
        return obj.patient.profile.full_name if hasattr(obj.patient, "profile") else obj.patient.email

    def get_therapist_name(self, obj) -> str:
        return str(obj.therapist)


class AdminAppointmentStatusSerializer(serializers.Serializer):
    """Serializer for admin status override on appointments."""

    status = serializers.ChoiceField(choices=Appointment.Status.choices)
    reason = serializers.CharField(required=False, allow_blank=True, default="")


# ─── Admin Therapist Update Serializer ────────────────────────────────────────


class AdminTherapistUpdateSerializer(serializers.Serializer):
    bio = serializers.CharField(allow_blank=True, required=False)
    specialties = serializers.ListField(child=serializers.UUIDField(), allow_empty=True, required=False)
    consultation_fee = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    is_available = serializers.BooleanField(required=False)
    years_of_experience = serializers.IntegerField(min_value=0, required=False)
    license_number = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def update(self, instance: Therapist, validated_data):
        if "bio" in validated_data:
            instance.bio = validated_data["bio"]
        if "consultation_fee" in validated_data:
            instance.consultation_fee = validated_data["consultation_fee"]
        if "is_available" in validated_data:
            instance.is_available = validated_data["is_available"]
        if "years_of_experience" in validated_data:
            instance.years_of_experience = validated_data["years_of_experience"]
        if "license_number" in validated_data:
            instance.license_number = validated_data["license_number"]
        if "specialties" in validated_data:
            ids = validated_data["specialties"]
            instance.specialties.set(Specialty.objects.filter(id__in=ids))
        instance.save()
        return instance
