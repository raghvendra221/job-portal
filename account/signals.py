
from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import User, SeekerProfile, RecruiterProfile
from django.urls import reverse
from account.utils import send_custom_email
from django.conf import settings
from job.models import Job

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_seeker:
            SeekerProfile.objects.create(user=instance)
        elif instance.is_recruiter:
            RecruiterProfile.objects.create(user=instance)




@receiver(post_save, sender=Job)
def send_job_post_email(sender, instance, created, **kwargs):
    """Send a welcome email when a new user account is created."""
    if created:
        recruiter=instance.recruiter
        # Define email context
        context = {
            'user': recruiter,
            'job': instance,
            # 'job_url':settings.SITE_DOMAIN + reverse('job_detail', args=[instance.id]),
            'dashboard_url': settings.SITE_DOMAIN + reverse('recruiter-dashboard'),
        }
        send_custom_email(
            subject="Your Job Post is Now Live!",
            template_name="account/job_post_email.html",
            context=context,
            to_email=recruiter.email,
        )

@receiver(post_save, sender=Job)
def notify_seekers_matched_job(sender, instance, created, **kwargs):
    if created:
        if not instance.skills:
            return  # No skills specified for the job
        job_skills = [skill.strip().lower() for skill in instance.skills.split(',')]
        seekers = SeekerProfile.objects.all()

        for seeker in seekers:
            # Skip seekers who haven’t filled skills
            if not seeker.skills:
                continue
            seeker_skills = [s.strip().lower() for s in seeker.skills.split(',')]
            if any(skill in seeker_skills for skill in job_skills):
                context = {
                    'user': seeker.user,
                    'job': instance,
                    'job_url': settings.SITE_DOMAIN + reverse('job_detail', args=[instance.id]),
                }
                send_custom_email(
                    subject=f"New {instance.title} Job Matching Your Skills!",
                    template_name="account/job_alert_email.html",
                    context=context,
                    to_email=seeker.user.email,
                )


