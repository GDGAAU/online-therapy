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
POST  /api/v1/therapy/appointments/<id>/reschedule/ → Reschedule
"""
from google.auth.transport.requests import Request
from account.email import send_appointment_email
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
from datetime import timezone as dt_timezone  


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
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["therapists"], summary="List therapists")
    def get(self, request):
        queryset = (
            Therapist.objects.select_related("user__profile")
            .prefetch_related("specialties")
            .filter(is_available=True)
        )

        specialty = request.query_params.get("specialty")
        if specialty:
            queryset = queryset.filter(specialties__slug=specialty)

        serializer = TherapistListSerializer(
            queryset,
            many=True,
            context={"request": request}
        )
        return Response({"results": serializer.data, "count": queryset.count()})


class TherapistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["therapists"], summary="Therapist detail")
    def get(self, request, pk):
        therapist = get_object_or_404(
            Therapist.objects.select_related("user__profile").prefetch_related("specialties"),
            pk=pk,
        )
        serializer = TherapistDetailSerializer(therapist, context={"request": request})
        return Response(serializer.data)


class TherapistAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["therapists"], summary="Therapist availability")
    def get(self, request, pk):
        from datetime import datetime, timedelta, time
        import datetime as dt

        start_date = request.query_params.get("from")
        end_date = request.query_params.get("to")

        if not start_date or not end_date:
            return Response(
                {"error": "from and to query params are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()

        if (end_date - start_date).days > 60:
            return Response(
                {"error": {"code": "RANGE_TOO_LARGE"}},
                status=status.HTTP_400_BAD_REQUEST
            )

        therapist = get_object_or_404(Therapist, pk=pk)

        appointments = Appointment.objects.filter(
            therapist=therapist,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
            scheduled_at__date__gte=start_date,
            scheduled_at__date__lte=end_date
        )

        result = {}

        current_date = start_date
        while current_date <= end_date:
            day_slots = []

            start_time = datetime.combine(current_date, time(8, 0))
            end_time = datetime.combine(current_date, time(18, 0))

            slot_time = start_time

            while slot_time < end_time:
                slot_end = slot_time + timedelta(minutes=50)

                is_available = True

                for appt in appointments:
                    appt_start = appt.scheduled_at
                    appt_end = appt_start + timedelta(minutes=appt.duration_minutes)

                    if slot_time < appt_end and slot_end > appt_start:
                        is_available = False
                        break

                if is_available:
                    day_slots.append({
                        "start_at": slot_time.isoformat(),
                        "end_at": slot_end.isoformat(),
                        "is_available": True
                    })

                slot_time = slot_end

            result[str(current_date)] = day_slots
            current_date += timedelta(days=1)

        return Response(result)


class AppointmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
    tags=["appointments"],
    responses=AppointmentSerializer(many=True),
)

        
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
    
    
    @extend_schema(
    tags=["appointments"],
    request=CreateAppointmentSerializer,
    responses=AppointmentSerializer,
)

    def post(self, request):
        serializer = CreateAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        therapist = serializer.validated_data["therapist_id"]
        scheduled_at = serializer.validated_data["scheduled_at"]
        duration = 50

        existing = Appointment.objects.filter(
            therapist=therapist,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        )

        new_end = scheduled_at + timedelta(minutes=duration)

        for appt in existing:
            appt_end = appt.scheduled_at + timedelta(minutes=appt.duration_minutes)

            if scheduled_at < appt_end and new_end > appt.scheduled_at:
                return Response(
                    {"error": "CONFLICT: overlapping appointment exists"}, 
                    status=status.HTTP_409_CONFLICT, 
                )

        appointment = Appointment.objects.create(
            patient=request.user,
            therapist=therapist,
            scheduled_at=scheduled_at,
            appointment_type=serializer.validated_data["appointment_type"],
            reason=serializer.validated_data.get("reason", ""),
        )

        try:
            send_appointment_email("booked", appointment)
        except Exception:
            pass

        return Response(
            AppointmentSerializer(appointment, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AppointmentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
    tags=["appointments"],
    responses=AppointmentSerializer,
)

    def _get_appointment(self, request, pk):
        return get_object_or_404(
            Appointment.objects.select_related("therapist__user__profile"),
            pk=pk,
            patient=request.user,
        )

    def get(self, request, pk):
        appointment = self._get_appointment(request, pk)
        return Response(AppointmentSerializer(appointment, context={"request": request}).data)


class CancelAppointmentView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
    tags=["appointments"],
    request=CancelAppointmentSerializer,
    responses={"200": {"message": "Appointment cancelled successfully."}},
)
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)

        if not appointment.can_cancel():
            return Response(
                {"error": {"code": "CANNOT_CANCEL"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CancelAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment.status = Appointment.Status.CANCELLED
        appointment.cancellation_reason = serializer.validated_data.get("reason", "")
        appointment.save(update_fields=["status", "cancellation_reason", "updated_at"])

        try:
            send_appointment_email("cancelled", appointment)
        except Exception:
            pass

        return Response({"message": "Appointment cancelled successfully."})


class AppointmentRescheduleView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
    tags=["appointments"],
    request=RescheduleAppointmentSerializer,
    responses=AppointmentSerializer,
)

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)

        serializer = RescheduleAppointmentSerializer(
            data=request.data,
            context={"appointment": appointment}
        )
        serializer.is_valid(raise_exception=True)

        scheduled_at = serializer.validated_data["scheduled_at"]
        duration = appointment.duration_minutes

        existing = Appointment.objects.filter(
            therapist=appointment.therapist,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).exclude(id=appointment.id)

        new_end = scheduled_at + timedelta(minutes=duration)

        for appt in existing:
            appt_end = appt.scheduled_at + timedelta(minutes=appt.duration_minutes)

            if scheduled_at < appt_end and new_end > appt.scheduled_at:
                return Response(
                    {"error": "CONFLICT: overlapping appointment exists"}, 
                    status=status.HTTP_409_CONFLICT, 
                )

        appointment.scheduled_at = scheduled_at

        if "appointment_type" in serializer.validated_data:
            appointment.appointment_type = serializer.validated_data["appointment_type"]

        appointment.save(update_fields=["scheduled_at", "appointment_type", "updated_at"])

        try:
            send_appointment_email("rescheduled", appointment)
        except Exception:
            pass

        return Response({
            "message": "Appointment rescheduled successfully.",
            "appointment": AppointmentSerializer(appointment, context={"request": request}).data
        })
    

class ConfirmAppointmentView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
    tags=["appointments"],
    responses={"200": {"message": "Appointment confirmed successfully."}},
)
    def post(self, request, pk):
        appointment = get_object_or_404(
            Appointment.objects.select_related("therapist__user"),
            pk=pk,
            therapist__user=request.user
        )
        
        if appointment.status != Appointment.Status.PENDING:
            return Response(
                {"error": {"code": "INVALID_STATUS", "detail": "Only pending appointments can be confirmed"}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = Appointment.Status.CONFIRMED
        appointment.save(update_fields=["status", "updated_at"])
        
        try:
            send_appointment_email("confirmed", appointment)
        except Exception:
            pass
        
        return Response({"message": "Appointment confirmed successfully."})


class GenerateMeetingLinkView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
    tags=["appointments"],
    responses=GenerateMeetingLinkSerializer,
)

    def post(self, request, pk):

        appointment = get_object_or_404(
            Appointment.objects.select_related("therapist__user", "patient"),
            pk=pk
        )

        if appointment.therapist.user_id != request.user.id:
            return Response(
                {"error": {"code": "FORBIDDEN"}},
                status=status.HTTP_403_FORBIDDEN
            )

        if appointment.status != Appointment.Status.CONFIRMED:
            return Response(
                {"error": {"code": "INVALID_STATUS"}},
                status=status.HTTP_400_BAD_REQUEST
            )

        if appointment.scheduled_at < timezone.now():
            return Response(
                {"error": {"code": "PAST_APPOINTMENT"}},
                status=status.HTTP_400_BAD_REQUEST
            )

        if appointment.meeting_link:
            return Response({"meeting_link": appointment.meeting_link})

        social_auth = request.user.social_auths.filter(provider="google").first()

        if not social_auth:
            return Response(
                {"error": {"code": "CALENDAR_NOT_CONNECTED"}},
                status=status.HTTP_403_FORBIDDEN
            )

        if not social_auth.access_token:
            return Response(
                {"error": {"code": "CALENDAR_PERMISSION_REQUIRED"}},
                status=status.HTTP_403_FORBIDDEN
            )

        creds = Credentials(
            token=social_auth.access_token,
            refresh_token=social_auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/calendar.events"],
        )

        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                social_auth.access_token = creds.token
                social_auth.save(update_fields=["access_token"])
            except Exception:
                return Response(
                    {"error": {"code": "TOKEN_REFRESH_FAILED"}},
                    status=status.HTTP_403_FORBIDDEN
                )

        service = build("calendar", "v3", credentials=creds)

        
        start = appointment.scheduled_at.astimezone(dt_timezone.utc)
        end = (appointment.scheduled_at + timedelta(
            minutes=appointment.duration_minutes
        )).astimezone(dt_timezone.utc)

        event = {
            "summary": f"Session with {appointment.patient.email}",
            "start": {
                "dateTime": start.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end.isoformat(),
                "timeZone": "UTC"
            },
            "conferenceData": {
                "createRequest": {
                    "requestId": str(appointment.id),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            },
        }

        try:
            created_event = service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1,
                sendNotifications=True
            ).execute()

        except HttpError:
            return Response(
                {"error": {"code": "GOOGLE_API_ERROR"}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        appointment.meeting_link = created_event.get("hangoutLink")

        if not appointment.meeting_link:
            return Response(
                {"error": {"code": "MEETING_LINK_MISSING"}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        appointment.save(update_fields=["meeting_link"])

        try:
            send_appointment_email("meeting_link", appointment)
        except Exception:
            pass

        return Response(
            GenerateMeetingLinkSerializer({
                "appointment_id": appointment.id,
                "meeting_link": appointment.meeting_link
            }).data
        )