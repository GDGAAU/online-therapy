"""therapy/urls.py"""
from django.urls import path
from .views import (
    TherapistListView,
    TherapistDetailView,
    AppointmentListCreateView,
    AppointmentDetailView,
    CancelAppointmentView,
)

urlpatterns = [
    path("therapists/", TherapistListView.as_view(), name="therapist-list"),
    path("therapists/<uuid:pk>/", TherapistDetailView.as_view(), name="therapist-detail"),
    path("appointments/", AppointmentListCreateView.as_view(), name="appointment-list-create"),
    path("appointments/<uuid:pk>/", AppointmentDetailView.as_view(), name="appointment-detail"),
    path("appointments/<uuid:pk>/cancel/", CancelAppointmentView.as_view(), name="appointment-cancel"),
]
