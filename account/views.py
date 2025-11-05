import hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from account.forms import SeekerSignUpForm, RecruiterSignUpForm, LoginForm, PasswordResetForm, SeekerProfileForm, RecruiterProfileForm
from account.models import User, SeekerProfile, RecruiterProfile
from django.contrib.auth.forms import SetPasswordForm
from application.forms import ApplicationForm
from application.models import Notification 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse
from account.utils import  send_custom_email
from job.models import Job
from application.models import Application
from core.decorators import role_required
from django.core.cache import cache
from jobportal.celery import app
from account.tasks import generate_seeker_dashboard_data
from account.tasks import get_resume_hash
from django.db.models import Q 
from django.http import JsonResponse  




def home(req):
    return render(req, 'account/home.html')

# Seeker Signup


def seeker_signup_view(request):
    if request.method == 'POST':
        form = SeekerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = reverse(
                'activate', kwargs={'uidb64': uidb64, 'token': token}
            )
            activation_url = f'{settings.SITE_DOMAIN}{activation_link}'

            send_custom_email(
                subject="Activate Your Account",
                template_name="account/activation_email.html",
                context={
                    "user": user,
                    "activation_url": activation_url,
                },
                to_email=user.email,
            )

            messages.success(
                request,
                'Registration successful! Please check your email to activate your account',
            )
            return redirect('login')

    else:
        form = SeekerSignUpForm()
    return render(request, 'account/seeker_signup.html', {'form': form})


# Recruiter Signup

def recruiter_signup_view(request):
    if request.method == 'POST':
        form = RecruiterSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = reverse(
                'activate', kwargs={'uidb64': uidb64, 'token': token}
            )
            activation_url = f'{settings.SITE_DOMAIN}{activation_link}'
            send_custom_email(
                subject="Activate Your Account",
                template_name="account/activation_email.html",
                context={
                    "user": user,
                    "activation_url": activation_url,
                },
                to_email=user.email,
            )

            messages.success(
                request,
                'Registration successful! Please check your email to activate your account',
            )
            return redirect('login')
    else:
        form = RecruiterSignUpForm()
    return render(request, 'account/recruiter_signup.html', {'form': form})


def activate_account(req, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if user.is_active:
            messages.warning(req, "This account has already been activate")

            return redirect('login')

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
             # ✅ Send welcome email once after activation
            context = {
                'user': user,
                'login_url': settings.SITE_DOMAIN + reverse('login'),
            }
            send_custom_email(
                subject="Welcome to JobPortal 🎉",
                template_name="account/WelcomeEmail.html",
                context=context,
                to_email=user.email,
            )
            messages.success(
                req, "Your account has been activated succesfully!!"
            )
            return redirect('login')
        else:
            messages.error(
                req, "The activation link is invalid or has expired.")

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(req, "Invalid activation link.")
        return redirect('login')
    

def resend_activation_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                messages.info(request, "Your account is already activated. Please log in.")
                return redirect('login')

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = reverse(
                'activate', kwargs={'uidb64': uidb64, 'token': token})
            activation_url = f'{settings.SITE_DOMAIN}{activation_link}'

            send_custom_email(
                subject="Activate Your Job Portal Account",
                template_name="account/activation_email.html",
                context={"user": user, "activation_url": activation_url},
                to_email=user.email,
            )

            messages.success(request, "A new activation link has been sent to your email.")
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect('login')

    return render(request, 'account/resend_activation.html')


def password_reset(req):
    if req.method == "POST":
        form =PasswordResetForm(req.POST)
        if form.is_valid():
            email=form.cleaned_data.get('email')
            user =User.objects.filter(email=email).first()
            if user:
                uidb64=urlsafe_base64_encode(force_bytes(user.pk))
                token= default_token_generator.make_token(user)
                reset_url=reverse(
                'password-reset-confirm',kwargs={'uidb64':uidb64,'token':token}
            )
            absolute_reset_url=f"{req.build_absolute_uri(reset_url)}"
            send_custom_email(
                subject="Password Reset Request",
                template_name="account/reset_pass_email.html",
                context={"user": user, "reset_url": absolute_reset_url},
                to_email=user.email,
            )
            messages.success(req,'We have sent you a password rest link.Please check your email.')

            return redirect('login')
    else:
        form=PasswordResetForm()
    return render(req,'account/pass_reset.html',{'form':form})

def password_reset_confirm(req,uidb64,token):
    try:
        uid =force_str(urlsafe_base64_decode(uidb64))
        user =User.objects.get(pk=uid)
        if not default_token_generator.check_token(user,token):
            messages.error(req,('This link has expired or is invalid'))
            return redirect('password-reset')
        if req.method == "POST":
            form = SetPasswordForm(user,req.POST)
            if form.is_valid():
                form.save()
            # Here you would normally set the user's new password
                messages.success(req,'Your password has been successfully reser')
                return redirect('login')  # redirect to a success page
            
        else:
            form = SetPasswordForm(user)
        return render(req,'account/pass_reset_confirmation.html',{'form':form,'uidb64':uidb64,'token':token})
    

    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        messages.error(req,'An error ocuured.Please try again later.')
        return redirect('password-reset')



# Login

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # xhecking if user exist in User moder
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(
                    request, "You are not registered. Please sign up first.")
                return render(request, 'account/home.html')
            
            if not user_obj.is_active:
                messages.warning(
                    request,
                    "Your account is not activated yet. Please check your email for the activation link. "
                    "If you didn’t receive one, you can resend it below."
                )
                
                return render(request, 'account/login.html', {'form': form})    
            # authentication
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if user.is_recruiter:
                    return redirect('recruiter-dashboard')
                else:
                    return redirect('seeker-dashboard')
            else:
                messages.error(request, "Invalid email or password")
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

# Logout


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')





@role_required('seeker')
def seeker_dashboard_view(request):
    """Show seeker dashboard or wait for Celery background data"""
    user = request.user
    seeker_profile = getattr(user, "seekerprofile", None)

    if not seeker_profile:
        return render(request, "account/layout/seeker_dashboard.html", {"error": "No seeker profile found"})

    resume_hash = get_resume_hash(seeker_profile)
    resume_key = f"resume_analysis_{user.id}_{resume_hash}"
    jobs_key = f"recommended_jobs_{user.id}_{resume_hash}"
    insight_key = f"ai_insight_{user.id}_{resume_hash}"

    resume_data = cache.get(resume_key)
    recommended_jobs = cache.get(jobs_key)
    ai_insight = cache.get(insight_key)

    # Jobs already applied (for "Applied" button)
    applied_jobs = list(Application.objects.filter(seeker=user).values_list("job_id", flat=True))
    query =request.GET.get('q','').strip()

    #  If cache empty  run Celery and show waiting message
    if not resume_data or not recommended_jobs or not ai_insight:
        task = generate_seeker_dashboard_data.delay(user.id)
        jobs_sample=Job.objects.all()
        if query:
            jobs_sample = jobs_sample.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(skills__icontains=query) |
                Q(location__icontains=query)
            )
        jobs_sample = jobs_sample.exclude(id__in=applied_jobs).order_by('-created_at')[:12]
        return render(
            request,
            "account/layout/seeker_dashboard.html",
            {
                 "loading": True,
                "message": "⏳ AI is analyzing your resume... please wait a few seconds.",
                "task_id": task.id,
                "jobs": jobs_sample,
                "applied_jobs": applied_jobs,
                "search_query": query,
            },
        )

    # If cached → show full dashboard
    resume_score = resume_data.get("score", 0) if isinstance(resume_data, dict) else 0
    if isinstance(recommended_jobs, list):
        recommended_jobs = [job for job in recommended_jobs if job.get("match_score", 0) ]
    
    #apply search filter for ai recommended jobs
    if query:
        recommended_jobs = [
            job for job in recommended_jobs
            if query.lower() in job.get("title", "").lower() or
               query.lower() in job.get("skills","").lower() or
               query.lower() in job.get("description","").lower() or
               query.lower() in job.get("location","").lower()
        ]
    
    # All jobs excluding applied ones
    all_jobs = Job.objects.exclude(id__in=applied_jobs).order_by('-created_at')
    if query:
        all_jobs = all_jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(skills__icontains=query) |
            Q(location__icontains=query)
        )
    all_jobs = all_jobs.order_by('-created_at')
    
    no_recommended_jobs = len(recommended_jobs) == 0

    return render(
        request,
        "account/layout/seeker_dashboard.html",
        {
            "resume_score": resume_score,
            "resume_data": resume_data,
            "recommended_jobs": recommended_jobs,
            "no_recommended_jobs": no_recommended_jobs,
            "ai_insight": ai_insight,
            "applied_jobs": applied_jobs,
            "jobs": all_jobs,
            "loading": False,
            "search_query": query,
        },
    )


@role_required('seeker')
def my_applications(request):
    seeker = request.user
    applications = Application.objects.filter(
        seeker=seeker).select_related('job')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)
       # Filter and count applications by status
    accepted_count = applications.filter(status__iexact='Accepted').count()
    pending_count = applications.filter(status__iexact='Pending').count()
    rejected_count = applications.filter(status__iexact='Rejected').count()
    applications.filter(is_seen=False).update(is_seen=True)
    context = {'applications': applications,
                'accepted_count': accepted_count,   
                'pending_count': pending_count,
                  'rejected_count': rejected_count
               }
    # return render(request, 'application/my_applications.html', context)
    return render(request, 'application/layout/my_applications.html', context)


@role_required('seeker')
def apply_job(request, job_id):
    seeker = request.user
    job = get_object_or_404(Job, id=job_id)

    # Prevent duplicate application
    if Application.objects.filter(seeker=seeker, job=job).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('seeker-dashboard')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES, job=job)
        if form.is_valid():
            application = form.save(commit=False)
            application.seeker = seeker
            application.job = job
            # Create notification for recruiter
            Notification.objects.create(
                sender=seeker,
                recipient=job.recruiter,
                message=f"{seeker.name} applied for your job '{job.title}'."
            )
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('seeker-dashboard')
    # Check if already applied
    else:
        form = ApplicationForm(job=job)
    return render(request, 'application/layout/apply_job.html', {'form': form, 'job': job})

def mark_all_read(request):
    Notification.objects.filter(recruiter=request.user, is_read=False).update(is_read=True)
    return redirect('recruiter-dashboard')



# Profile View and Edit

@login_required
def profile_view(request):
    user = request.user

    if user.is_seeker:
        profile,created = SeekerProfile.objects.get_or_create(user=user)
        form_class = SeekerProfileForm
        dashboard_url = 'seeker-dashboard'
    elif user.is_recruiter:
        profile,created= RecruiterProfile.objects.get_or_create(user=user)
        form_class = RecruiterProfileForm
        dashboard_url = 'recruiter-dashboard'
    else:
        messages.error(request, "Profile is not available for this account.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if 'remove_picture' in request.POST:
            if profile.profile_picture:
                profile.profile_picture.delete(save=True)
            messages.success(request, "Profile picture removed successfully.")
            return redirect(dashboard_url)
        if form.is_valid():
            form.save()
            if user.is_seeker:
                if not profile.skills or profile.skills.strip() == "":
                    messages.warning(request, "⚠️ Add your skills to receive job alert emails.")
                else:
                    messages.success(request, "✅ Profile updated successfully!")
            else:
                messages.success(request, "✅ Profile updated successfully!")
            return redirect(dashboard_url)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = form_class(instance=profile)

   
    # return render(request, 'account/profile.html', {
    #     'form': form, 'user': user,
    # })
    return render(request, 'account/layout/profile.html', {
        'form': form, 'user': user,
    })



@role_required('seeker')
def ai_insight_view(request):
    user = request.user
    seeker_profile = getattr(user, "seekerprofile", None)
    if not seeker_profile:
        return render(request, "account/layout/ai_insight.html", {"error": "No seeker profile found"})

    #  Use the same cache key pattern as in Celery task
    resume_hash = get_resume_hash(seeker_profile)
    resume_cache_key = f"resume_analysis_{user.id}_{resume_hash}"
    insight_cache_key = f"ai_insight_{user.id}_{resume_hash}"

    #  Fetch from cache first (to stay consistent with dashboard)
    resume_data = cache.get(resume_cache_key)
    ai_insight = cache.get(insight_cache_key)

    #  Fallback to database if cache expired
    if not resume_data:
        resume_data = {
            "score": seeker_profile.resume_score or 0,
            "feedback": seeker_profile.ai_feedback or "",
            "matched_jobs": [],
        }

    if not ai_insight:
        ai_insight =  "<p class='text-muted small'>AI insight not available yet. Please refresh your dashboard.</p>"
    

    resume_score = float(resume_data.get("score") or 0)
    print("DEBUG (ai_insight_view): resume_score =", resume_score)

    context = {
        "resume_score": resume_score,
        "resume_feedback": resume_data.get("feedback", ""),
        "matched_jobs": resume_data.get("matched_jobs", []),
        "ai_insight": ai_insight,
        "user_name":  user.name,
    }
    print("DEBUG → resume_data:", resume_data)
    print("DEBUG → resume_score:", resume_data.get("score", 0))
    return render(request, "account/layout/ai_insight.html", context)

# @role_required('recruiter')
def recruiter_search_jobs(request):
    query = request.GET.get("q", "").strip()
    user = request.user
    jobs = Job.objects.filter(recruiter=user)
    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(location__icontains=query)

    data = {
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "salary": job.salary,
                "experience_required": job.experience_required,
                "description": job.description[:100] + "..." if job.description else "",
            }
            for job in jobs
        ]
    }
    return JsonResponse(data)


@role_required('seeker')
def seeker_live_search(request):
    # allow empty queries
    query = request.GET.get("q", "").strip()
    user = request.user

    # jobs user hasn't applied to
    applied_jobs = list(Application.objects.filter(seeker=user).values_list("job_id", flat=True))

    jobs_qs = Job.objects.exclude(id__in=applied_jobs).order_by("-created_at")
    if query:
        jobs_qs = jobs_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(skills__icontains=query) |
            Q(location__icontains=query)
        )

    jobs = jobs_qs[:50]  # limit for safety

    data = {
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "location": job.location or "",
                "salary": job.salary or "",
                "experience_required": job.experience_required or "",
                "description": (job.description[:120] + "...") if job.description else "",
            }
            for job in jobs
        ]
    }
    return JsonResponse(data)



