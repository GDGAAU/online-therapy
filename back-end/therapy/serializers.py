"""therapy/serializers.py"""
from rest_framework import serializers
from django.utils import timezone  
from .models import Therapist, Appointment, Specialty


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ["id", "name", "slug"]


class TherapistListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    name = serializers.SerializerMethodField()
    specialties = SpecialtySerializer(many=True, read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Therapist
        fields = [
            "id", "name", "specialties", "years_of_experience",
            "consultation_fee", "avatar_url",  
        ]

    def get_name(self, obj) -> str:
        return f"Dr. {obj.user.profile.full_name}"

    def get_avatar_url(self, obj) -> str | None:
        profile = obj.user.profile
        if profile.avatar:
            request = self.context.get("request")
            return request.build_absolute_uri(profile.avatar.url) if request else None
        return None


class TherapistDetailSerializer(TherapistListSerializer):
    """Full serializer for detail views — includes bio."""

    class Meta(TherapistListSerializer.Meta):
        fields = TherapistListSerializer.Meta.fields + ["bio", "license_number"]


class AppointmentSerializer(serializers.ModelSerializer):
    therapist_name = serializers.SerializerMethodField()
    therapist_specialty = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id", "therapist", "therapist_name", "therapist_specialty",
            "status", "appointment_type", "scheduled_at", "duration_minutes",
            "reason", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def get_therapist_name(self, obj) -> str:
        return str(obj.therapist)

    def get_therapist_specialty(self, obj) -> list[str]:
        return [s.name for s in obj.therapist.specialties.all()]


class CreateAppointmentSerializer(serializers.Serializer):
    therapist_id = serializers.UUIDField()
    scheduled_at = serializers.DateTimeField()
    appointment_type = serializers.ChoiceField(choices=Appointment.AppointmentType.choices)
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate_therapist_id(self, value):
        try:
            # ensures only available therapists can be booked
            return Therapist.objects.get(id=value, is_available=True)
        except Therapist.DoesNotExist:
            raise serializers.ValidationError("Therapist not found or unavailable.")


class CancelAppointmentSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class RescheduleAppointmentSerializer(serializers.Serializer):
    scheduled_at = serializers.DateTimeField()
    appointment_type = serializers.ChoiceField(
        choices=Appointment.AppointmentType.choices, required=False
    )

    def validate_scheduled_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("New appointment time must be in the future.")
        return value

    def validate(self, attrs):
        appointment = self.context.get("appointment")
        if not appointment or not appointment.can_reschedule():
            raise serializers.ValidationError("This appointment cannot be rescheduled.")
        return attrs