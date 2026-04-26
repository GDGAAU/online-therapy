"""
account/views.py
=================
Profile endpoints used alongside djoser auth.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .models import CustomUser, Profile, SocialAuth
from .serializers import ProfileSerializer, UpdateProfileSerializer


class MeView(APIView):
    """Retrieve and update the current user's profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, context={"request": request})
        return Response(serializer.data)

    def patch(self, request):
        profile = request.user.profile
        serializer = UpdateProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProfileSerializer(profile, context={"request": request}).data)


class LogoutView(APIView):
    """Blacklist the refresh token on logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Logged out."}, status=status.HTTP_200_OK)


class GoogleLoginView(APIView):
    """Authenticate/signup users with Google ID token and return JWT token pair."""

    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("id_token") or request.data.get("token")
        if not token:
            return Response({"detail": "Google id_token is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not settings.GOOGLE_CLIENT_ID:
            return Response(
                {"detail": "Google OAuth is not configured on the server."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            return Response({"detail": "Invalid Google token."}, status=status.HTTP_400_BAD_REQUEST)

        email = (idinfo.get("email") or "").strip().lower()
        if not email:
            return Response({"detail": "Google account email is missing."}, status=status.HTTP_400_BAD_REQUEST)

        user, _ = CustomUser.objects.get_or_create(
            email=email,
            defaults={"is_active": True},
        )

        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])

        profile, _ = Profile.objects.get_or_create(user=user)
        given_name = idinfo.get("given_name") or ""
        family_name = idinfo.get("family_name") or ""

        changed_fields: list[str] = []
        if given_name and not profile.first_name:
            profile.first_name = given_name
            changed_fields.append("first_name")
        if family_name and not profile.last_name:
            profile.last_name = family_name
            changed_fields.append("last_name")
        if changed_fields:
            profile.save(update_fields=changed_fields)

        provider_user_id = str(idinfo.get("sub") or "")
        if provider_user_id:
            SocialAuth.objects.update_or_create(
                provider=SocialAuth.GOOGLE,
                provider_user_id=provider_user_id,
                defaults={"user": user,"access_token": request.data.get("access_token"), "refresh_token": request.data.get("refresh_token"), "token_expires_at": request.data.get("token_expires_at") or None},
                
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
