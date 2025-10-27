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
                    "activation_link": activation_url,
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

# seeker dashboard functioning work


@role_required('seeker')
def seeker_dashboard_view(request):
    user = request.user
    # Jobs the user has already applied to
    applied_jobs = Application.objects.filter(
        seeker=user).values_list('job_id', flat=True)
    # Jobs available to apply (not applied yet)
    jobs = Job.objects.exclude(id__in=applied_jobs)

    unseen_notifications = Application.objects.filter(
        seeker=user,
        is_seen=False,
        status__in=['Accepted', 'Rejected']
    )

    context = {
        'jobs': jobs,
        'applied_jobs': applied_jobs,
        'unseen_notifications': unseen_notifications
    }
    return render(request, 'account/seeker_dashboard.html', context)


@role_required('seeker')
def my_applications(request):
    seeker = request.user
    applications = Application.objects.filter(
        seeker=seeker).select_related('job')
    applications.filter(is_seen=False).update(is_seen=True)
    context = {'applications': applications}
    return render(request, 'application/my_applications.html', context)


@role_required('recruiter')
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
            recruiter = job.recruiter
            message = f"{seeker.name} applied for your job '{job.title}'."
            Notification.objects.create(recruiter=recruiter, message=message)
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('seeker-dashboard')
    # Check if already applied
    else:
        form = ApplicationForm(job=job)
    return render(request, 'application/apply_job.html', {'form': form, 'job': job})

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
    elif user.is_recruiter:
        profile,created= RecruiterProfile.objects.get_or_create(user=user)
        form_class = RecruiterProfileForm
    else:
        messages.error(request, "Profile is not available for this account.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = form_class(instance=profile)

   
    return render(request, 'account/profile.html', {
        'form': form, 'user': user,
    })


