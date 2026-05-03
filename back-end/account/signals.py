"""account/signals.py — auto-create Profile when a new user is saved."""
import logging
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .models import CustomUser, Profile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance: CustomUser, created: bool, **kwargs):
    """Create an empty Profile whenever a new CustomUser is created."""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=CustomUser)
def ensure_therapist_profile_for_staff(sender, instance: CustomUser, **kwargs):
    """Ensure staff (non-superuser) users always have a Therapist profile."""
    if instance.is_staff and not instance.is_superuser:
        Therapist = apps.get_model("therapy", "Therapist")
        Therapist.objects.get_or_create(user=instance)


@receiver(post_save, sender=CustomUser)
def blacklist_outstanding_tokens_on_deactivation(sender, instance: CustomUser, created: bool, **kwargs):
    """Blacklist outstanding JWT tokens immediately when a user is deactivated."""
    if created or instance.is_active:
        return

    outstanding_tokens = OutstandingToken.objects.filter(
        user=instance,
        expires_at__gt=timezone.now(),
        blacklistedtoken__isnull=True,
    )
    for outstanding_token in outstanding_tokens:
        BlacklistedToken.objects.get_or_create(token=outstanding_token)
        logger.info(
            "Blacklisted outstanding token %s for deactivated user %s",
            outstanding_token.jti,
            instance.email,
        )
