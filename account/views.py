from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from account.forms import SeekerSignUpForm, RecruiterSignUpForm, LoginForm
from application.forms import ApplicationForm
from account.models import User
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse
from account.utils import send_activation_email,send_reset_password_email
from job.models import Job
from application.models import Application


def home(req):
    return render(req,'account/home.html')

# Seeker Signup
def seeker_signup_view(request):
    if request.method == 'POST':
        form = SeekerSignUpForm(request.POST)
        if form.is_valid():
            user=form.save()


            uidb64=urlsafe_base64_encode(force_bytes(user.pk))
            token= default_token_generator.make_token(user)
            activation_link=reverse(
                'activate',kwargs={'uidb64':uidb64,'token':token}
            )
            activation_url=f'{settings.SITE_DOMAIN}{activation_link}'
            send_activation_email(user,activation_url)

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
            user=form.save()


            uidb64=urlsafe_base64_encode(force_bytes(user.pk))
            token= default_token_generator.make_token(user)
            activation_link=reverse(
                'activate',kwargs={'uidb64':uidb64,'token':token}
            )
            activation_url=f'{settings.SITE_DOMAIN}{activation_link}'
            send_activation_email(user,activation_url)

            messages.success(
                request,
                'Registration successful! Please check your email to activate your account',
                )
            return redirect('login')
    else:
        form = RecruiterSignUpForm()
    return render(request, 'account/recruiter_signup.html', {'form': form})




def activate_account(req,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user=User.objects.get(pk=uid)

        if user.is_active:
            messages.warning(req,"This account has already been activate")

            return redirect('login')
        
        if default_token_generator.check_token(user,token):
            user.is_active=True
            user.save()
            messages.success(
                req,"Your account has been activated succesfully!!"
            )
            return redirect('login')
        else:
            messages.error(req,"The activation link is invalid or has expired.")


    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        messages.error(req,"Invalid activation link.")
        return redirect('login')

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
                messages.error(request, "You are not registered. Please sign up first.")
                return render(request, 'account/home.html')
            #authentication
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if user.is_recruiter:
                    return redirect('recruiter-dashboard')
                else:
                    return redirect('seeker-dashboard')
            else:
                messages.error(request,"Invalid email or password")
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

# Logout
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

#seeker dashboard functioning work

@login_required
def seeker_dashboard_view(request):
     user= request.user
      # Jobs the user has already applied to
     applied_jobs = Application.objects.filter(seeker=user).values_list('job_id', flat=True)
     # Jobs available to apply (not applied yet)
     jobs = Job.objects.exclude(id__in=applied_jobs)
      
     
     context = {
        'jobs': jobs,
        'applied_jobs': applied_jobs,
    }
     return render(request, 'account/seeker_dashboard.html', context)

@login_required
def my_applications(request):
    user=request.user
    applications = Application.objects.filter(seeker=user)
    context = {'applications': applications}
    return render(request, 'application/my_applications.html', context)


@login_required
def apply_job(request, job_id):
    seeker=request.user
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
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('seeker-dashboard')
    # Check if already applied
    else:
        form = ApplicationForm(job=job)
    return render(request, 'application/apply_job.html', {'form': form, 'job': job})