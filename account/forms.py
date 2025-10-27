
from django import forms
from django.contrib.auth.forms import UserCreationForm #if we usercreationform then we dont need to check the password1 and password2 is same or not
from account.models import User, SeekerProfile, RecruiterProfile   

class SeekerSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'city', 'password1', 'password2']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
          
        self.fields['email'].widget.attrs.update({
            'class': 'form-control signup-input',
            'placeholder': '📧 Email address',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
        self.fields['name'].widget.attrs.update({
            'class': 'form-control signup-input',
            'placeholder': '👤 Full Name',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
        self.fields['city'].widget.attrs.update({
            'class': 'form-control signup-input',
            'placeholder': '🏙️ City',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control signup-input',
            'placeholder': '🔒 Password',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control signup-input',
            'placeholder': '🔒 Confirm Password',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
        # Add Bootstrap classes to each field
        # for field_name, field in self.fields.items():
        #     field.widget.attrs['class'] = 'form-control'
        #     field.widget.attrs['placeholder'] = field.label

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_seeker = True
        user.is_recruiter = False
        # user.is_active = True  # Email verification can be added later
        if commit:
            user.save()
        return user

class RecruiterSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'city', 'password1', 'password2']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['email'].widget.attrs.update({
            'class': 'form-control signup-input',
            'placeholder': '📧 Email address',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
        self.fields['name'].widget.attrs.update({
            'class': 'form-control signup-input',
            'placeholder': '👤 Full Name',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
        self.fields['city'].widget.attrs.update({
            'class': 'form-control signup-input',
            'placeholder': '🏙️ City',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control signup-input',
            'placeholder': '🔒 Password',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control signup-input',
            'placeholder': '🔒 Confirm Password',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
        # Add Bootstrap classes
        # for field_name, field in self.fields.items():
        #     field.widget.attrs['class'] = 'form-control'
        #     field.widget.attrs['placeholder'] = field.label

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_recruiter = True
        user.is_seeker = False
          # Email verification can be added later
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={ 'class': 'form-control signup-input',
            'placeholder': '📧 Email address',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={ 'class': 'form-control signup-input',
            'placeholder': '🔒 Password',
            'style': 'background: rgba(28,35,49,0.7); color:#fff; border-radius:8px; border:none; margin-bottom:14px; font-size: 1.08em;'})
    )


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email'
        }),
        label="Email"
    )
    def clean_email(self):
        email=self.cleaned_data.get('email')
        #check if a user with this exail exist
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('' \
            'No account is associated with this email')
        return email




class SeekerProfileForm(forms.ModelForm):
    class Meta:
        model = SeekerProfile
        fields = ['phone', 'location', 'profile_picture', 'resume', 'skills']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['phone', 'location', 'profile_picture', 'company_name', 'company_website', 'designation']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
