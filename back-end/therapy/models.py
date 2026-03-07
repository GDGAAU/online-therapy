"""
therapy/models.py
==================
Core domain models for the therapy platform.

Models:
- Therapist: Therapist profiles linked to users
- Appointment: Booking records
- AppointmentNote: Medical notes per appointment
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Specialty(models.Model):
    """A medical/therapeutic specialty (e.g., Psychologist, Psychiatrist)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "specialties"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Therapist(models.Model):
    """
    Therapist profile linked to a user account.
    A Therapist IS a user but with additional professional info.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="therapist_profile",
    )
    specialties = models.ManyToManyField(Specialty, related_name="therapists", blank=True)
    years_of_experience = models.PositiveSmallIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    license_number = models.CharField(max_length=100, blank=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    bio = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__profile__first_name"]

    def __str__(self) -> str:
        return f"Dr. {self.user.profile.full_name}"


class Appointment(models.Model):
    """An appointment booking between a patient and a therapist."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")
        NO_SHOW = "no_show", _("No Show")

    class AppointmentType(models.TextChoices):
        IN_PERSON = "in_person", _("In Person")
        VIDEO = "video", _("Video Call")
        PHONE = "phone", _("Phone Call")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    therapist = models.ForeignKey(
        Therapist,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    appointment_type = models.CharField(
        max_length=20, choices=AppointmentType.choices, default=AppointmentType.VIDEO
    )

    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=50)

    reason = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_at"]
        indexes = [
            models.Index(fields=["patient", "status"]),
            models.Index(fields=["therapist", "scheduled_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.patient.email} → {self.therapist} @ {self.scheduled_at:%Y-%m-%d %H:%M}"

    def can_cancel(self) -> bool:
        return self.status in [self.Status.PENDING, self.Status.CONFIRMED]

    def can_reschedule(self) -> bool:
        return self.status in [self.Status.PENDING, self.Status.CONFIRMED]
