from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from application.models import Application
from job.models import Job
from django.views.generic import ListView



from django.contrib.auth.decorators import login_required
from .models import Application, Job

@login_required
def view_applications(request):
    # Get the recruiter
    recruiter = request.user
    
    # Get all jobs posted by this recruiter
    jobs_posted = Job.objects.filter(recruiter=recruiter)
    
    # Get all applications for those jobs
    applications = Application.objects.filter(job__in=jobs_posted).select_related('seeker', 'job')
    
    context = {
        'applications': applications
    }
    return render(request, 'application/view_applications.html', context)
