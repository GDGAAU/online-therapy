from django.urls import path
from .views import (
    AdminTherapistListCreateView,
    AdminTherapistDetailView,
    AdminUserListView,
    AdminUserDetailView,
    AdminUserActivateView,
    AdminUserDeactivateView,
    AdminAppointmentListView,
    AdminAppointmentStatusView,
)

urlpatterns = [
    # Therapist endpoints
    path("therapists/", AdminTherapistListCreateView.as_view(), name="admin-therapist-list-create"),
    path("therapists/<uuid:pk>/", AdminTherapistDetailView.as_view(), name="admin-therapist-detail"),
    
    # User endpoints
    path("users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("users/<uuid:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("users/<uuid:pk>/activate/", AdminUserActivateView.as_view(), name="admin-user-activate"),
    path("users/<uuid:pk>/deactivate/", AdminUserDeactivateView.as_view(), name="admin-user-deactivate"),

    # Appointment endpoints
    path("appointments/", AdminAppointmentListView.as_view(), name="admin-appointment-list"),
    path("appointments/<uuid:pk>/status/", AdminAppointmentStatusView.as_view(), name="admin-appointment-status"),
]
