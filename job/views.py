from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from job.models import Job
from application.models import Notification
from application.models import Application
from job.forms import JobForm
from django.contrib import messages
from core.decorators import role_required



@method_decorator(role_required('recruiter'), name='dispatch')

class PostJobView(View):
    def get(self, request):
        form = JobForm()
        # return render(request, 'job/post_job.html', {'form': form})
        return render(request, 'job/layout/post_job.html', {'form': form})

    def post(self, request):
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('recruiter-dashboard')
        # return render(request, 'job/post_job.html', {'form': form})
        return render(request, 'job/layout/post_job.html', {'form': form})
    
@role_required('seeker')
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'job/job_detail.html', {'job': job})

    
@role_required('recruiter')
def recruiter_dashboard_view(request):
 
    #Fetch unread notifications for the recruiter
    # notifications = Notification.objects.filter(recruiter=request.user, is_read=False).order_by('-created_at')[:10]
    # unread_count = notifications.count()
    base_qs = Notification.objects.filter(recipient=request.user,is_read=False).order_by('-created_at')
    unread_count = base_qs.count()
    notifications = base_qs[:10]
    # Jobs posted by the recruiter
    jobs = Job.objects.filter(recruiter=request.user)
    context={
        'notifications': notifications, 
        'unread_count': unread_count,
        'jobs':jobs
        }

    return render(request, 'account/layout/recruiter_dashboard.html', context)

@role_required('recruiter') 
def edit_job(request,job_id):
    job=get_object_or_404(Job,id=job_id,recruiter=request.user)
    if request.method =='POST':
        form=JobForm(request.POST,instance=job)
        if form.is_valid():
            form.save()
            return redirect('recruiter-dashboard')
    else:
        form=JobForm(instance=job)
    # return render(request,'job/edit_form.html',{'form':form,'job':job})
    return render(request,'job/layout/edit_form.html',{'form':form,'job':job})

@role_required('recruiter')
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('recruiter-dashboard')

