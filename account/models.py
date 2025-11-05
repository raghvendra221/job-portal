# accounts/models.py
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.conf import settings    

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_recruiter', True)
        extra_fields.setdefault('is_seeker', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)
    is_seeker = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser




class BaseProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.name


class SeekerProfile(BaseProfile):
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_score = models.FloatField(default=0, blank=True, null=True)
    ai_feedback = models.TextField(blank=True, null=True)  # <— ADD THIS
    skills = models.CharField(
        max_length=255,
        blank=True,  # allow saving blank
        null=True,
        help_text="Comma-separated list of your skills")

    def __str__(self):
        return f"{self.user.name} (Seeker)"
    def save(self, *args, **kwargs):
        if self.pk:
            old = SeekerProfile.objects.filter(pk=self.pk).first()
            if old and old.resume != self.resume:
                from account.tasks import generate_seeker_dashboard_data
                print("🔁 Resume changed → re-running AI analysis task...")
                generate_seeker_dashboard_data.delay(self.user.id)
        super().save(*args, **kwargs)


class RecruiterProfile(BaseProfile):
    company_name = models.CharField(max_length=100, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.name} (Recruiter)"



