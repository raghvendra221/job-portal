
from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import User, SeekerProfile, RecruiterProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_seeker:
            SeekerProfile.objects.create(user=instance)
        elif instance.is_recruiter:
            RecruiterProfile.objects.create(user=instance)
