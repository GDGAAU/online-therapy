from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse

from .permissions import IsAdminOnly, IsAdminUser
from .serializers import (
    AdminTherapistCreateSerializer,
    AdminTherapistSerializer,
    AdminTherapistUpdateSerializer,
    UserAdminSerializer,
    UserAdminDetailSerializer,
)
from account.models import CustomUser
from therapy.models import Therapist


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
