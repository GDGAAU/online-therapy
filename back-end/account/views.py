"""
account/views.py
=================
Profile endpoints used alongside djoser auth.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import GoogleAuthSerializer, ProfileSerializer, UpdateProfileSerializer
from .models import CustomUser, Profile, SocialAuth
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed



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

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_token_str = serializer.validated_data["id_token"]

        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
            )

            email = idinfo.get("email")
            name = idinfo.get("name", "")
            google_id = idinfo.get("sub")

            if not email:
                raise AuthenticationFailed("Google account has no email")

        except Exception:
            raise AuthenticationFailed("Invalid Google token")

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={"is_active": True},
        )

        if created:
            profile, _ = Profile.objects.get_or_create(user=user)
            parts = name.split()
            profile.first_name = parts[0] if parts else ""
            profile.last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
            profile.save()

        social_auth = SocialAuth.objects.filter(
            provider="google",
            provider_user_id=google_id
        ).first()

        if social_auth:
            # If already linked but to a different user → error
            if social_auth.user != user:
                raise AuthenticationFailed("This Google account is already linked to another user")
        else:
            SocialAuth.objects.create(
                provider="google",
                provider_user_id=google_id,
                user=user
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )