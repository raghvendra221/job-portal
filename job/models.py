from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Job(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    experience_required = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


        # New Fields — Recruiter’s required credentials
    require_resume = models.BooleanField(default=True)
    require_cover_letter = models.BooleanField(default=False)
    require_portfolio = models.BooleanField(default=False)
    require_github = models.BooleanField(default=False)

    def __str__(self):
        return self.title