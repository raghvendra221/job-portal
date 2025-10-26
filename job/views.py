from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from job.models import Job
from application.models import Application
from job.forms import JobForm
from django.contrib import messages


# ---------------- Recruiter Views ----------------
@method_decorator(login_required, name='dispatch')
class PostJobView(View):
    def get(self, request):
        form = JobForm()
        return render(request, 'job/post_job.html', {'form': form})

    def post(self, request):
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('recruiter-dashboard')
        return render(request, 'job/post_job.html', {'form': form})
    
@login_required
def recruiter_dashboard_view(request):
    # Show jobs posted by this recruiter
    jobs = Job.objects.filter(recruiter=request.user)
    return render(request, 'account/recruiter_dashboard.html', {'jobs': jobs})

def edit_job(request,job_id):
    job=get_object_or_404(Job,id=job_id,recruiter=request.user)
    if request.method =='POST':
        form=JobForm(request.POST,instance=job)
        if form.is_valid():
            form.save()
            return redirect('recruiter-dashboard')
    else:
        form=JobForm(instance=job)
    return render(request,'job/edit_form.html',{'form':form,'job':job})

def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('recruiter-dashboard')

