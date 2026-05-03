"""therapy/urls.py"""
from django.urls import path
from .views import (
    AppointmentRescheduleView,
    CompleteAppointmentView,
    ConfirmAppointmentView,
    CurrentTherapistProfileView,
    GenerateMeetingLinkView,
    SpecialtyListView,
    TherapistListView,
    TherapistDetailView,
    AppointmentListCreateView,
    AppointmentDetailView,
    CancelAppointmentView,
    TherapistAvailabilityView,
)

urlpatterns = [
    # therapist endpoints
    path("specialties/", SpecialtyListView.as_view(), name="specialty-list"),
    path("therapists/", TherapistListView.as_view(), name="therapist-list"),
    path("therapists/me/", CurrentTherapistProfileView.as_view(), name="current-therapist-profile"),
    path("therapists/<uuid:pk>/", TherapistDetailView.as_view(), name="therapist-detail"),
    path("appointments/", AppointmentListCreateView.as_view(), name="appointment-list-create"),

    # appointment endpoints
    path("appointments/<uuid:pk>/", AppointmentDetailView.as_view(), name="appointment-detail"),
    path("appointments/<uuid:pk>/confirm/", ConfirmAppointmentView.as_view(), name="appointment-confirm"),
    path("appointments/<uuid:pk>/complete/", CompleteAppointmentView.as_view(), name="appointment-complete"),
    path("appointments/<uuid:pk>/cancel/", CancelAppointmentView.as_view(), name="appointment-cancel"),
    path("appointments/<uuid:pk>/reschedule/", AppointmentRescheduleView.as_view(), name="appointment-reschedule"),
    path(
        "appointments/<uuid:pk>/generate-meeting-link/",
        GenerateMeetingLinkView.as_view(),
        name="appointment-generate-meeting-link"
    ),
    path(
        "therapists/<uuid:pk>/availability/",
        TherapistAvailabilityView.as_view(),
        name="therapist-availability"
    ),
]
