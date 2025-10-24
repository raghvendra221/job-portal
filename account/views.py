from django.shortcuts import render, redirect
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
            if user:
                login(request, user)
                if user.is_recruiter:
                    return redirect('recruiter-dashboard')
                else:
                    return redirect('seeker-dashboard')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

# Logout
@login_required
def logout_view(request):
    logout(request)
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
