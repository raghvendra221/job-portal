from django.db import models
from account.models import User
from job.models import Job
class Application(models.Model):
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    status_choices = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    github_link = models.URLField(blank=True, null=True)

    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.seeker.email} - {self.job.title}"



class Notification(models.Model):
    sender=models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    recipient=models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # ===== UPDATED / NEW FEATURE =====
    action_url = models.CharField(max_length=255, blank=True, null=True)
    # ===== UPDATED / NEW FEATURE =====
    
    def __str__(self):
        return f"Notification for {self.recipient.email}: {self.message[:40]}"

# ===== NEW FEATURE START =====
class Shortlist(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='shortlist')
    shortlisted_at = models.DateTimeField(auto_now_add=True)
    recruiter_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Shortlisted: {self.application.seeker.email} for {self.application.job.title}"
# ===== NEW FEATURE END =====
