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

    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    cover_letter = models.FileField(upload_to='cover_letters/', null=True, blank=True)
    portfolio = models.URLField(null=True, blank=True)
    github_link = models.URLField(null=True, blank=True)

    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.seeker.username} - {self.job.title}"



class Notification(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recruiter.username}: {self.message[:40]}"
