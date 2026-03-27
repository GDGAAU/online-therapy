"""
therapy/views.py
=================
Appointment and therapist management endpoints.
GET  /api/v1/therapy/therapists/                → List all therapists
GET  /api/v1/therapy/therapists/<id>/           → Therapist detail
GET  /api/v1/therapy/appointments/              → My appointments
POST /api/v1/therapy/appointments/              → Book an appointment
GET  /api/v1/therapy/appointments/<id>/         → Appointment detail
POST /api/v1/therapy/appointments/<id>/cancel/  → Cancel appointment
POST /api/v1/therapy/appointments/<id>/reschedule/ → Reschedule
"""


from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.utils import timezone  
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from core.settings.base import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from .serializers import GenerateMeetingLinkSerializer
from datetime import timedelta
from googleapiclient.errors import HttpError

from .models import Therapist, Appointment
from .serializers import (
    TherapistListSerializer,
    TherapistDetailSerializer,
    AppointmentSerializer,
    CreateAppointmentSerializer,
    CancelAppointmentSerializer,
    RescheduleAppointmentSerializer,  
)


class TherapistListView(APIView):
    """List all available therapists with optional filters."""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["therapists"], summary="List therapists")
    def get(self, request):
        queryset = (
            Therapist.objects.select_related("user__profile")
            .prefetch_related("specialties")
            .filter(is_available=True)
        )
        # Filter by specialty slug
        specialty = request.query_params.get("specialty")
        if specialty:
            queryset = queryset.filter(specialties__slug=specialty)
        serializer = TherapistListSerializer(queryset, many=True, context={"request": request})
        return Response({"results": serializer.data, "count": queryset.count()})


class TherapistDetailView(APIView):
    """Get a single therapist's full profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["therapists"], summary="Therapist detail")
    def get(self, request, pk):
        therapist = get_object_or_404(
            Therapist.objects.select_related("user__profile").prefetch_related("specialties"),
            pk=pk,
        )
        serializer = TherapistDetailSerializer(therapist, context={"request": request})
        return Response(serializer.data)


class AppointmentListCreateView(APIView):
    """List the current user's appointments or create a new one."""
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["appointments"], summary="List my appointments")
    def get(self, request):
        status_filter = request.query_params.get("status")
        queryset = (
            Appointment.objects.select_related("therapist__user__profile")
            .prefetch_related("therapist__specialties")
            .filter(patient=request.user)
        )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        serializer = AppointmentSerializer(queryset, many=True, context={"request": request})
        return Response({"results": serializer.data, "count": queryset.count()})

    @extend_schema(tags=["appointments"], summary="Book an appointment",request=CreateAppointmentSerializer)
    def post(self, request):
        serializer = CreateAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        therapist = serializer.validated_data["therapist_id"]

        # exact match conflict check
        if Appointment.objects.filter(
            therapist=therapist,
            scheduled_at=serializer.validated_data["scheduled_at"],
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).exists():
            return Response(
                {"error": "Therapist already has an appointment at this time."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment = Appointment.objects.create(
            patient=request.user,
            therapist=therapist,
            scheduled_at=serializer.validated_data["scheduled_at"],
            appointment_type=serializer.validated_data["appointment_type"],
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(
            AppointmentSerializer(appointment, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AppointmentDetailView(APIView):
    """Retrieve a single appointment belonging to the current user."""
    permission_classes = [IsAuthenticated]

    def _get_appointment(self, request, pk):
        return get_object_or_404(
            Appointment.objects.select_related("therapist__user__profile"),
            pk=pk,
            patient=request.user,
        )

    @extend_schema(tags=["appointments"], summary="Appointment detail")
    def get(self, request, pk):
        appointment = self._get_appointment(request, pk)
        return Response(AppointmentSerializer(appointment, context={"request": request}).data)


class CancelAppointmentView(APIView):
    """Cancel an appointment."""
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["appointments"], summary="Cancel appointment",request=CancelAppointmentSerializer)
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)
        if not appointment.can_cancel():
            return Response(
                {"error": {"code": "CANNOT_CANCEL", "message": f"Cannot cancel an appointment with status '{appointment.status}'.", "detail": None}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = CancelAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment.status = Appointment.Status.CANCELLED
        appointment.cancellation_reason = serializer.validated_data.get("reason", "")
        appointment.save(update_fields=["status", "cancellation_reason", "updated_at"])
        return Response({"message": "Appointment cancelled successfully."})


class AppointmentRescheduleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["appointments"], summary="Reschedule appointment",request=RescheduleAppointmentSerializer)
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)
        serializer = RescheduleAppointmentSerializer(data=request.data, context={"appointment": appointment})
        serializer.is_valid(raise_exception=True)

        # conflict check for new time slot
        if Appointment.objects.filter(
            therapist=appointment.therapist,
            scheduled_at=serializer.validated_data["scheduled_at"],
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).exclude(id=appointment.id).exists():
            return Response(
                {"error": "Therapist already has an appointment at this time."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.scheduled_at = serializer.validated_data["scheduled_at"]
        if "appointment_type" in serializer.validated_data:
            appointment.appointment_type = serializer.validated_data["appointment_type"]
        appointment.save(update_fields=["scheduled_at", "appointment_type", "updated_at"])

        return Response(
            {
                "message": "Appointment rescheduled successfully.",
                "appointment": AppointmentSerializer(appointment, context={"request": request}).data
            }
        )
    



  

class GenerateMeetingLinkView(APIView):
    """Generate a Google Meet link for a confirmed upcoming appointment."""
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["appointments"], summary="Generate Google Meet link", responses={200: GenerateMeetingLinkSerializer})
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)

        
        if appointment.therapist.user != request.user:
            return Response(
                {"error": "Only the assigned therapist can generate the meeting link."},
                status=status.HTTP_403_FORBIDDEN
            )

        if appointment.status != Appointment.Status.CONFIRMED:
            return Response(
                {"error": "Meeting link can only be generated for confirmed appointments."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if appointment.scheduled_at < timezone.now():
            return Response(
                {"error": "Cannot generate meeting link for past appointments."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            social_auth = request.user.social_auths.get(provider="google")
        except request.user.social_auths.model.DoesNotExist:
            return Response(
                {"error": "Google account not linked for this therapist."},
                status=status.HTTP_400_BAD_REQUEST
            )

       
        creds = Credentials(
            token=social_auth.token_hash,
            refresh_token=getattr(social_auth, "refresh_token", None),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/calendar.events"],
        )

        service = build("calendar", "v3", credentials=creds)
        event = {
            "summary": f"Session with {appointment.patient.email}",
            "start": {"dateTime": appointment.scheduled_at.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": (appointment.scheduled_at + timedelta(minutes=appointment.duration_minutes)).isoformat(), "timeZone": "UTC"},
            "conferenceData": {"createRequest": {"requestId": str(appointment.id)}},
        }

        try:
            created_event = service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1
            ).execute()
        except HttpError as e:
            return Response(
                {"error": f"Failed to create Google Meet link: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        appointment.meeting_link = created_event.get("hangoutLink")
        appointment.save(update_fields=["meeting_link"])

        serializer = GenerateMeetingLinkSerializer({
            "appointment_id": appointment.id,
            "meeting_link": appointment.meeting_link
        })
        return Response(serializer.data, status=status.HTTP_200_OK)