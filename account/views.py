from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from account.forms import SeekerSignUpForm, RecruiterSignUpForm, LoginForm


def home(req):
    return render(req,'account/home.html')

# Seeker Signup
def seeker_signup_view(request):
    if request.method == 'POST':
        form = SeekerSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
    else:
        form = SeekerSignUpForm()
    return render(request, 'account/seeker_signup.html', {'form': form})

# Recruiter Signup
def recruiter_signup_view(request):
    if request.method == 'POST':
        form = RecruiterSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Recruiter account created successfully! Please login.")
            return redirect('login')
    else:
        form = RecruiterSignUpForm()
    return render(request, 'account/recruiter_signup.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
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

# Dashboards
@login_required
def seeker_dashboard_view(request):
    if not request.user.is_seeker:
        return redirect('login')
    return render(request, 'account/seeker_dashboard.html')

@login_required
def recruiter_dashboard_view(request):
    if not request.user.is_recruiter:
        return redirect('login')
    return render(request, 'account/recruiter_dashboard.html')
