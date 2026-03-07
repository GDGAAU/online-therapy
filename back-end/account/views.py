from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.conf import settings
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from .models import Profile, User
from .serializers import ProfileSerializer
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from djoser import utils
from djoser.conf import settings as djoser_settings
from django.contrib.auth.tokens import default_token_generator

from google.oauth2 import id_token
from google.auth.transport import requests

User = get_user_model()


class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class ProfileSearchView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        query = self.kwargs.get(
            'query', '') or self.request.query_params.get('q', '')
        queryset = Profile.objects.select_related('user').all()

        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(occupation__icontains=query) |
                Q(location__icontains=query)
            ).distinct()

        return queryset.order_by('first_name', 'last_name')


class ProfileDetailView(generics.RetrieveAPIView):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    lookup_field = 'username'

    def get_object(self):
        username = self.kwargs.get(self.lookup_field)
        return get_object_or_404(Profile, user__username=username)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        is_me = request.user.is_authenticated and instance.user == request.user

        return Response({
            "is_me": is_me,
            "profile": serializer.data
        })


class GoogleAuthAPIView(APIView):
    def post(self, request):
        token = request.data.get("id_token")

        if not token:
            return Response(
                {"detail": "id_token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Verify token with Google
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            return Response(
                {"detail": "Invalid or expired Google token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        email = idinfo.get("email")
        first_name = idinfo.get("given_name", "")
        last_name = idinfo.get("family_name", "")

        if not email:
            return Response(
                {"detail": "Google account has no email"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "auth_provider": "google",
                "is_verified": False,
            }
        )

        # 3. If newly created → finalize setup
        if created:
            user.set_unusable_password()
            user.save()

            # Update profile
            profile = user.profile
            profile.first_name = first_name
            profile.last_name = last_name
            profile.save()

        # 4. Issue JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK
        )
    
class ResendActivationView(APIView):
    """
    Resend activation email if the user exists and is inactive.
    """

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "If this email is registered and not activated, an email was sent."})

        if user.is_active:
            return Response({"detail": "This account is already active."})

        # Generate UID and token
        uid = utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)

        # Generate activation URL using Djoser pattern and request
        activation_path = djoser_settings.ACTIVATION_URL.format(
            uid=uid, token=token)
        activation_url = request.build_absolute_uri(
            f"/{activation_path}")  # ✅ full URL

        context = {
            "user": user,
            "activation_url": activation_url,  # full link
        }

        # Send email
        email_class = djoser_settings.EMAIL.activation
        email_instance = email_class(request, context)
        email_instance.send(user.email)

        return Response({"detail": "Activation email sent successfully."})


class CustomLoginView(APIView):
    """
    Custom login:
    - Returns JWT tokens for active users.
    - If user exists but inactive → tell them + provide resend link.
    - If invalid credentials → return standard error.
    """

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(password):
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_active:
            return Response(
                {
                    "detail": "Your account is not activated. Please activate your account before logging in."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK
        )