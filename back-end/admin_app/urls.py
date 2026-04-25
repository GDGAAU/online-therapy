from django.urls import path
from .views import AdminTherapistListCreateView, AdminTherapistDetailView

urlpatterns = [
    path("therapists/", AdminTherapistListCreateView.as_view(), name="admin-therapist-list-create"),
    path("therapists/<uuid:pk>/", AdminTherapistDetailView.as_view(), name="admin-therapist-detail"),
]
