from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from application.models import Application
from job.models import Job
from django.views.generic import ListView

# Apply for a job (FBV)
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if Application.objects.filter(job=job, seeker=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
    else:
        Application.objects.create(job=job, seeker=request.user)
        messages.success(request, "Job application submitted successfully!")
    return redirect('seeker-dashboard')

# List all applicants for a job (CBV)
class JobApplicantsListView(ListView):
    model = Application
    template_name = 'application/job_applicants.html'
    context_object_name = 'applications'

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        job = get_object_or_404(Job, id=job_id, recruiter=self.request.user)
        return job.applications.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = get_object_or_404(Job, id=self.kwargs['job_id'])
        return context

# Update application status (FBV)
def update_application_status(request, app_id, status):
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    if status in ['Accepted', 'Rejected']:
        application.status = status
        application.save()
        messages.success(request, f"Application status updated to {status}.")
    else:
        messages.error(request, "Invalid status.")
    return redirect('job_applicants', job_id=application.job.id)
