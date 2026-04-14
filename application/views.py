from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from application.models import Application
from job.models import Job
from application.forms import ApplicationStatusForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from application.models import Notification

from django.db.models import Count, Q
from account.models import SeekerProfile
from .models import Shortlist


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
            # ===== UPDATED / NEW FEATURE =====
            "action_url": n.action_url or "#"
            # ===== UPDATED / NEW FEATURE =====
        })

    return JsonResponse({"count": len(data), "notifications": data})



@login_required
def mark_notifications_read(request):
    """Mark all unseen notifications as read for the logged-in user"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"success": True})


# ===== NEW FEATURE START =====


@login_required
def toggle_shortlist(request, application_id):
    """Toggle a candidate's shortlist status."""
    application = get_object_or_404(Application, id=application_id)
    
    if request.user != application.job.recruiter:
        return JsonResponse({"error": "Not authorized"}, status=403)
        
    shortlist_obj = Shortlist.objects.filter(application=application).first()
    
    if shortlist_obj:
        shortlist_obj.delete()
        action = "removed"
    else:
        Shortlist.objects.create(application=application)
        action = "added"
        
    return JsonResponse({"action": action, "application_id": application_id})

@login_required
def candidate_ai_match(request, application_id):
    """Fetch AI match score for a specific application's seeker"""
    application = get_object_or_404(Application, id=application_id)
    if request.user != application.job.recruiter:
        return JsonResponse({"error": "Not authorized"}, status=403)
    
    profile = getattr(application.seeker, 'seekerprofile', None)
    score = profile.resume_score if profile else 0
    feedback = profile.ai_feedback if profile else "No AI analysis available."
    
    return JsonResponse({
        "score": score,
        "feedback": feedback
    })

@login_required
def recruiter_dashboard_stats(request):
    """Fetch total jobs, total apps, and shortlisted candidates"""
    user = request.user
    if not getattr(user, 'is_recruiter', False):
        return JsonResponse({"error": "Not authorized"}, status=403)
        
    jobs = Job.objects.filter(recruiter=user)
    total_jobs = jobs.count()
    total_applications = Application.objects.filter(job__in=jobs).count()
    shortlisted = Shortlist.objects.filter(application__job__in=jobs).count()
    
    return JsonResponse({
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "shortlisted": shortlisted
    })

# ===== NEW FEATURE =====
from core.decorators import role_required

@role_required('recruiter')
def recruiter_applicants_view(request):
    """Isolated page for recruiter to manage all applications across jobs."""
    applications = Application.objects.filter(job__recruiter=request.user).order_by('-applied_at')
    
    # Optional filtering
    status_filter = request.GET.get('status')
    if status_filter == 'shortlisted':
        applications = applications.filter(shortlist__isnull=False)

    search_query = request.GET.get('q')
    if search_query:
        applications = applications.filter(
            Q(seeker__name__icontains=search_query) |
            Q(job__title__icontains=search_query)
        )
        
    order_by_date = request.GET.get('order')
    if order_by_date == 'oldest':
        applications = applications.order_by('applied_at')

    context = {
        'applications': applications,
        'search_query': search_query,
        'status_filter': status_filter,
        'order_by_date': order_by_date
    }
    return render(request, 'application/layout/recruiter_applicants.html', context)

# ===== NEW FEATURE =====
import json
from account.utils import generate_job_description_with_gemini
from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def generate_job_description(request):
    """API endpoint to generate AI job descriptions during posting."""
    if not getattr(request.user, 'is_recruiter', False):
        return JsonResponse({"error": "Not authorized"}, status=403)
        
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get('title', '')
            skills = data.get('skills', '')
            experience = data.get('experience', '')
            
            description = generate_job_description_with_gemini(title, skills, experience)
            
            return JsonResponse({"description": description})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)
# ===== NEW FEATURE =====

# ===== NEW FEATURE END =====
