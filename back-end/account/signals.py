"""account/signals.py — auto-create Profile when a new user is saved."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance: CustomUser, created: bool, **kwargs):
    """Create an empty Profile whenever a new CustomUser is created."""
    if created:
        Profile.objects.get_or_create(user=instance)
