# tasks/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Creates or updates the user profile when the user instance is saved.
    """
    # Create profile if it doesn't exist
    if created:
        Profile.objects.create(user=instance)
    # Update profile for user if user is saved
    else:
        instance.profile.save()

