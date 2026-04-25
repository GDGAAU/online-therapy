from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse

from .permissions import IsAdminOnly
from .serializers import (
    AdminTherapistCreateSerializer,
    AdminTherapistSerializer,
    AdminTherapistUpdateSerializer,
)
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
