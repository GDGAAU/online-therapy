"""account/signals.py — auto-create Profile when a new user is saved."""
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, Profile


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
