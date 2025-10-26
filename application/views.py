from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from application.models import Application
from job.models import Job
from django.contrib.auth.decorators import login_required


@login_required
def view_applicants(request,job_id):
    
    recruiter = request.user
    job=get_object_or_404(Job,id=job_id,recruiter=recruiter)
    
    # Get all jobs posted by this recruiter
    # jobs_posted = Job.objects.filter(recruiter=recruiter)
    
    # Get all applications for those jobs
    applications = Application.objects.filter(job=job)
    
    context = {
        'applications': applications,
        'job':job
    }
    return render(request, 'application/view_applicants.html', context)
