from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q, Count
from django.utils.dateparse import parse_datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse

from .permissions import IsAdminOnly, IsAdminUser
from .serializers import (
    AdminTherapistCreateSerializer,
    AdminTherapistSerializer,
    AdminTherapistUpdateSerializer,
    UserAdminSerializer,
    UserAdminDetailSerializer,
    AdminAppointmentSerializer,
    AdminAppointmentStatusSerializer,
)
from account.models import CustomUser
from therapy.models import Therapist, Appointment


LIST_PARAMETERS = [
    OpenApiParameter(name="q", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.STR, description="Search by email, first name or last name"),
    OpenApiParameter(name="status", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.STR, description="Filter by status: active, inactive, available, unavailable"),
    OpenApiParameter(name="page_size", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.INT, description="Page size override"),
]


class AdminTherapistListCreateView(APIView):
    permission_classes = [IsAdminOnly]

    @extend_schema(tags=["admin", "therapists"], summary="List therapists (admin)", parameters=LIST_PARAMETERS, responses={200: AdminTherapistSerializer(many=True)})
    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get("page_size", None) or paginator.page_size

        queryset = Therapist.objects.select_related("user__profile").prefetch_related("specialties").filter(user__is_active=True)

        # Status filters
        status_q = request.query_params.get("status")
        if status_q == "active":
            queryset = queryset.filter(user__is_active=True)
        elif status_q == "inactive":
            queryset = queryset.filter(user__is_active=False)
        elif status_q == "available":
            queryset = queryset.filter(is_available=True)
        elif status_q == "unavailable":
            queryset = queryset.filter(is_available=False)

        # Search (by email or name)
        q = request.query_params.get("q")
        if q:
            queryset = queryset.filter(
                Q(user__email__icontains=q) |
                Q(user__profile__first_name__icontains=q) |
                Q(user__profile__last_name__icontains=q)
            ).distinct()

        page = paginator.paginate_queryset(queryset, request)
        serializer = AdminTherapistSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(tags=["admin", "therapists"], summary="Create therapist (admin)", request=AdminTherapistCreateSerializer, responses={201: AdminTherapistSerializer})
    def post(self, request):
        serializer = AdminTherapistCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        therapist = serializer.save()
        out = AdminTherapistSerializer(therapist, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)


class AdminTherapistDetailView(APIView):
    permission_classes = [IsAdminOnly]

    @extend_schema(tags=["admin", "therapists"], summary="Get therapist detail (admin)", responses=AdminTherapistSerializer)
    def get(self, request, pk):
        therapist = get_object_or_404(Therapist.objects.select_related("user__profile").prefetch_related("specialties"), pk=pk)
        serializer = AdminTherapistSerializer(therapist, context={"request": request})
        return Response(serializer.data)

    @extend_schema(tags=["admin", "therapists"], summary="Update therapist (admin)", request=AdminTherapistUpdateSerializer, responses=AdminTherapistSerializer)
    def patch(self, request, pk):
        therapist = get_object_or_404(Therapist, pk=pk)
        serializer = AdminTherapistUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        therapist = serializer.update(therapist, serializer.validated_data)
        return Response(AdminTherapistSerializer(therapist, context={"request": request}).data)

    @extend_schema(tags=["admin", "therapists"], summary="Deactivate therapist (admin)", responses={204: OpenApiResponse(description="User deactivated")})
    def delete(self, request, pk):
        therapist = get_object_or_404(Therapist, pk=pk)
        user = therapist.user
        user.is_active = False
        user.save(update_fields=["is_active"]) 
        return Response(status=status.HTTP_204_NO_CONTENT)


# User management views

USER_LIST_PARAMETERS = [
    OpenApiParameter(name="is_active", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.BOOL, description="Filter by is_active status"),
    OpenApiParameter(name="user_type", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.STR, description="Filter by user type: admin, therapist, patient"),
    OpenApiParameter(name="search", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.STR, description="Search by email or full name"),
    OpenApiParameter(name="page_size", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.INT, description="Page size override"),
]


class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=["admin", "users"], summary="List users (admin)", parameters=USER_LIST_PARAMETERS, responses={200: UserAdminSerializer(many=True)})
    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get("page_size", None) or paginator.page_size

        queryset = CustomUser.objects.select_related("profile").all()

        # Filter by is_active
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            is_active_bool = is_active.lower() in ("true", "1", "yes")
            queryset = queryset.filter(is_active=is_active_bool)

        # Filter by user_type
        user_type = request.query_params.get("user_type")
        if user_type == "admin":
            queryset = queryset.filter(is_superuser=True)
        elif user_type == "therapist":
            queryset = queryset.filter(is_staff=True, is_superuser=False)
        elif user_type == "patient":
            queryset = queryset.filter(is_staff=False, is_superuser=False)

        # Search by email or full name
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(profile__first_name__icontains=search) |
                Q(profile__last_name__icontains=search)
            ).distinct()

        page = paginator.paginate_queryset(queryset, request)
        serializer = UserAdminSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=["admin", "users"], summary="Get user detail (admin)", responses=UserAdminDetailSerializer)
    def get(self, request, pk):
        user = get_object_or_404(CustomUser.objects.select_related("profile"), pk=pk)
        serializer = UserAdminDetailSerializer(user, context={"request": request})
        return Response(serializer.data)


class AdminUserActivateView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=["admin", "users"], summary="Activate user (admin)", responses={200: UserAdminSerializer})
    def patch(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(UserAdminSerializer(user, context={"request": request}).data)


class AdminUserDeactivateView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=["admin", "users"], summary="Deactivate user (admin)", responses={200: UserAdminSerializer})
    def patch(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(UserAdminSerializer(user, context={"request": request}).data)


# ─── Appointment management views ─────────────────────────────────────────────

APPOINTMENT_LIST_PARAMETERS = [
    OpenApiParameter(name="status", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.STR, description="Filter by appointment status: pending, confirmed, completed, cancelled, no_show"),
    OpenApiParameter(name="therapist_id", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.UUID, description="Filter by therapist UUID"),
    OpenApiParameter(name="patient_id", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.UUID, description="Filter by patient UUID"),
    OpenApiParameter(name="from", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.DATETIME, description="Filter appointments scheduled on or after this datetime (ISO 8601)"),
    OpenApiParameter(name="to", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.DATETIME, description="Filter appointments scheduled on or before this datetime (ISO 8601)"),
    OpenApiParameter(name="page", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.INT, description="Page number"),
    OpenApiParameter(name="page_size", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.INT, description="Page size (default 25)"),
]


class AdminAppointmentPagination(PageNumberPagination):
    """Custom paginator that defaults to 25 items per page."""
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class AdminAppointmentListView(APIView):
    """
    GET /api/v1/admin/appointments/
    List all appointments across the platform with filters and aggregate stats.
    Requires IsAdminUser permission.
    """
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["admin", "appointments"],
        summary="List all appointments (admin)",
        parameters=APPOINTMENT_LIST_PARAMETERS,
        responses={200: AdminAppointmentSerializer(many=True)},
    )
    def get(self, request):
        queryset = (
            Appointment.objects
            .select_related("patient__profile", "therapist__user__profile")
            .prefetch_related("therapist__specialties")
            .all()
        )

        # ── Filter by status ──────────────────────────────────────────────
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # ── Filter by therapist_id ────────────────────────────────────────
        therapist_id = request.query_params.get("therapist_id")
        if therapist_id:
            queryset = queryset.filter(therapist_id=therapist_id)

        # ── Filter by patient_id ──────────────────────────────────────────
        patient_id = request.query_params.get("patient_id")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        # ── Filter by date range (from / to) ──────────────────────────────
        date_from = request.query_params.get("from")
        if date_from:
            parsed = parse_datetime(date_from)
            if parsed is None:
                # Try as date-only string (e.g. "2026-04-01")
                from django.utils.dateparse import parse_date
                d = parse_date(date_from)
                if d:
                    from django.utils import timezone as tz
                    from datetime import datetime, time
                    parsed = tz.make_aware(datetime.combine(d, time.min))
            if parsed:
                queryset = queryset.filter(scheduled_at__gte=parsed)

        date_to = request.query_params.get("to")
        if date_to:
            parsed = parse_datetime(date_to)
            if parsed is None:
                from django.utils.dateparse import parse_date
                d = parse_date(date_to)
                if d:
                    from django.utils import timezone as tz
                    from datetime import datetime, time
                    parsed = tz.make_aware(datetime.combine(d, time.max))
            if parsed:
                queryset = queryset.filter(scheduled_at__lte=parsed)

        # ── Compute aggregate stats on the filtered queryset ──────────────
        stats = queryset.aggregate(
            total=Count("id"),
            pending_count=Count("id", filter=Q(status=Appointment.Status.PENDING)),
            confirmed_count=Count("id", filter=Q(status=Appointment.Status.CONFIRMED)),
            cancelled_count=Count("id", filter=Q(status=Appointment.Status.CANCELLED)),
        )

        # ── Paginate ──────────────────────────────────────────────────────
        paginator = AdminAppointmentPagination()
        page_size_param = request.query_params.get("page_size")
        if page_size_param:
            paginator.page_size = int(page_size_param)

        page = paginator.paginate_queryset(queryset, request)
        serializer = AdminAppointmentSerializer(page, many=True, context={"request": request})

        # Build response with stats in meta
        response = paginator.get_paginated_response(serializer.data)
        response.data["meta"] = {
            "total": stats["total"],
            "pending_count": stats["pending_count"],
            "confirmed_count": stats["confirmed_count"],
            "cancelled_count": stats["cancelled_count"],
        }
        return response


class AdminAppointmentStatusView(APIView):
    """
    PATCH /api/v1/admin/appointments/<id>/status/
    Override appointment status (admin force-confirm, force-cancel, mark no_show).
    Follows the same pattern as normal status changes for notification consistency.
    Requires IsAdminUser permission.
    """
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["admin", "appointments"],
        summary="Override appointment status (admin)",
        request=AdminAppointmentStatusSerializer,
        responses={200: AdminAppointmentSerializer},
    )
    def patch(self, request, pk):
        appointment = get_object_or_404(
            Appointment.objects.select_related("patient__profile", "therapist__user__profile"),
            pk=pk,
        )

        serializer = AdminAppointmentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        reason = serializer.validated_data.get("reason", "")

        old_status = appointment.status
        appointment.status = new_status

        # Persist cancellation reason when admin force-cancels
        update_fields = ["status", "updated_at"]
        if new_status == Appointment.Status.CANCELLED and reason:
            appointment.cancellation_reason = reason
            update_fields.append("cancellation_reason")

        appointment.save(update_fields=update_fields)

        return Response(
            {
                "message": f"Appointment status changed from '{old_status}' to '{new_status}'.",
                "appointment": AdminAppointmentSerializer(appointment, context={"request": request}).data,
            }
        )
