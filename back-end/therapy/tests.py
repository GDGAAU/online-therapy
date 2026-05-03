from datetime import timedelta

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from account.models import CustomUser
from therapy.models import Appointment, Specialty, Therapist


class TherapistDiscoveryTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.anxiety = Specialty.objects.create(name="Anxiety Counseling", slug="anxiety-counseling")
        self.depression = Specialty.objects.create(name="Depression", slug="depression")

        self.lena_anxiety = self.create_therapist(
            email="lena.anxiety@example.com",
            first_name="Lena",
            last_name="Ortiz",
            specialties=[self.anxiety],
        )
        self.lena_depression = self.create_therapist(
            email="lena.depression@example.com",
            first_name="Lena",
            last_name="Morris",
            specialties=[self.depression],
        )
        self.maya_anxiety = self.create_therapist(
            email="maya@example.com",
            first_name="Maya",
            last_name="Green",
            specialties=[self.anxiety],
        )

    def create_therapist(
        self,
        *,
        email,
        first_name,
        last_name,
        specialties,
        bio="Experienced therapist.",
        license_number="LIC-123",
        consultation_fee="150.00",
    ):
        user = CustomUser.objects.create_user(email=email, password="TestPassword123")
        user.profile.first_name = first_name
        user.profile.last_name = last_name
        user.profile.save(update_fields=["first_name", "last_name"])

        therapist = Therapist.objects.create(
            user=user,
            bio=bio,
            license_number=license_number,
            consultation_fee=consultation_fee,
        )
        therapist.specialties.set(specialties)
        return therapist

    def response_ids(self, response):
        return {item["id"] for item in response.data["results"]}

    def test_search_filters_therapists_by_name(self):
        response = self.client.get(reverse("therapist-list"), {"search": "lena"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.response_ids(response),
            {str(self.lena_anxiety.id), str(self.lena_depression.id)},
        )

    def test_search_no_match_returns_empty_list(self):
        response = self.client.get(reverse("therapist-list"), {"search": "not-a-therapist"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_specialty_filter_uses_slug(self):
        response = self.client.get(reverse("therapist-list"), {"specialty": "anxiety-counseling"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.response_ids(response),
            {str(self.lena_anxiety.id), str(self.maya_anxiety.id)},
        )

    def test_search_and_specialty_are_combined_with_and(self):
        response = self.client.get(
            reverse("therapist-list"),
            {"search": "lena", "specialty": "anxiety-counseling"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.response_ids(response), {str(self.lena_anxiety.id)})

    def test_therapist_detail_exposes_profile_completeness(self):
        incomplete = self.create_therapist(
            email="incomplete@example.com",
            first_name="Noah",
            last_name="Incomplete",
            specialties=[],
            bio="",
            license_number="LIC-999",
            consultation_fee="120.00",
        )

        response = self.client.get(reverse("therapist-detail", args=[incomplete.id]))

        self.assertEqual(response.status_code, 200)
        self.assertIs(response.data["is_profile_complete"], False)

    def test_profile_complete_requires_all_required_fields(self):
        self.assertIs(self.lena_anxiety.is_profile_complete, True)

        self.lena_anxiety.license_number = ""
        self.lena_anxiety.save(update_fields=["license_number"])

        self.assertIs(self.lena_anxiety.is_profile_complete, False)

    def test_current_therapist_profile_can_be_read_and_updated(self):
        self.client.force_authenticate(user=self.lena_anxiety.user)

        response = self.client.get(reverse("current-therapist-profile"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.lena_anxiety.id))
        self.assertIs(response.data["is_profile_complete"], True)

        response = self.client.patch(
            reverse("current-therapist-profile"),
            {
                "bio": "Updated therapist bio.",
                "specialties": ["depression"],
                "is_available": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["bio"], "Updated therapist bio.")
        self.assertFalse(response.data["is_available"])
        self.assertEqual(
            {specialty["slug"] for specialty in response.data["specialties"]},
            {"depression"},
        )

    def test_therapist_appointment_list_returns_current_therapist_sessions(self):
        patient = CustomUser.objects.create_user(email="patient@example.com", password="TestPassword123")
        patient.profile.first_name = "Patient"
        patient.profile.last_name = "One"
        patient.profile.save(update_fields=["first_name", "last_name"])

        appointment = Appointment.objects.create(
            patient=patient,
            therapist=self.lena_anxiety,
            status=Appointment.Status.CONFIRMED,
            scheduled_at=timezone.now() + timedelta(days=1),
            appointment_type=Appointment.AppointmentType.VIDEO,
            reason="Initial intake",
        )
        Appointment.objects.create(
            patient=patient,
            therapist=self.lena_depression,
            status=Appointment.Status.CONFIRMED,
            scheduled_at=timezone.now() + timedelta(days=2),
            appointment_type=Appointment.AppointmentType.PHONE,
        )

        self.client.force_authenticate(user=self.lena_anxiety.user)
        response = self.client.get(reverse("appointment-list-create"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(appointment.id))
        self.assertEqual(response.data["results"][0]["patient_name"], "Patient One")

    def test_therapist_can_complete_confirmed_appointment(self):
        patient = CustomUser.objects.create_user(email="complete-patient@example.com", password="TestPassword123")
        appointment = Appointment.objects.create(
            patient=patient,
            therapist=self.lena_anxiety,
            status=Appointment.Status.CONFIRMED,
            scheduled_at=timezone.now() + timedelta(days=1),
            appointment_type=Appointment.AppointmentType.VIDEO,
        )

        self.client.force_authenticate(user=self.lena_anxiety.user)
        response = self.client.post(reverse("appointment-complete", args=[appointment.id]))

        self.assertEqual(response.status_code, 200)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.COMPLETED)


class SpecialtyListTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_specialty_list_is_public_and_cached(self):
        Specialty.objects.create(name="Anxiety", slug="anxiety")
        Specialty.objects.create(name="Family Therapy", slug="family-therapy")

        response = self.client.get(reverse("specialty-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Cache-Control"], "max-age=60")
        self.assertEqual(
            {item["slug"] for item in response.data["results"]},
            {"anxiety", "family-therapy"},
        )
