from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from application.models import Application
from job.models import Job
from application.forms import ApplicationStatusForm
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



@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if request.user != application.job.recruiter:
        messages.error(request, "Not authorized.")
        return redirect('recruiter-dashboard')
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            app=form.save(commit=False)
            app.is_seen = False  # Mark as unseen for the seeker
            app.save()  
            messages.success(request, "Status updated successfully!")

            # Optionally: send email to seeker
            # send_email_to_seeker(application.seeker.email, application.status, application.job.title)

        return redirect('view-applicants', job_id=application.job.id)
    else:
        form = ApplicationStatusForm(instance=application)

    return render(request, 'application/update_status.html', {'form': form, 'application': application})