
from django import forms
from django.contrib.auth.forms import UserCreationForm #if we usercreationform then we dont need to check the password1 and password2 is same or not
from .models import User

class SeekerSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'city', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_seeker = True
        user.is_recruiter = False
        user.is_active = True  # Email verification can be added later
        if commit:
            user.save()
        return user

class RecruiterSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'city', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_recruiter = True
        user.is_seeker = False
        user.is_active = True
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
