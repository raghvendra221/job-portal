from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from application.models import Application
from job.models import Job
from application.forms import ApplicationStatusForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from application.models import Notification


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
    # return render(request, 'application/view_applicants.html', context)
    return render(request, 'application/layout/view_applicants.html', context)



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
            Notification.objects.create(
                sender=request.user,
                recipient=app.seeker,
                message=f"Your application for '{app.job.title}' has been updated to {app.status}"
            ) 
            messages.success(request, "Status updated successfully!")


        return redirect('view-applicants', job_id=application.job.id)
    else:
        form = ApplicationStatusForm(instance=application)

    return render(request, 'application/layout/update_status.html', {'form': form, 'application': application})



@login_required
def get_unseen_notifications(request):
    """Return unseen notifications as JSON for AJAX polling"""
    user = request.user

    unseen_notifications = (
        Notification.objects.filter(
            recipient=user,
            is_read=False
        )
        .order_by('-created_at')[:10]  # slice LAST, not before filtering
    )

    data = []
    for n in unseen_notifications:
        data.append({
            "message": n.message,
            "created_at": n.created_at.strftime("%b %d, %I:%M %p"),
        })

    return JsonResponse({"count": len(data), "notifications": data})



@login_required
def mark_notifications_read(request):
    """Mark all unseen notifications as read for the logged-in user"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"success": True})
