# application/forms.py
from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter', 'portfolio', 'github_link']
        widgets = {
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'cover_letter': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'portfolio': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Portfolio URL'}),
            'github_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'GitHub URL'}),
        }

    def __init__(self, *args, **kwargs):
        job = kwargs.pop('job', None)
        super().__init__(*args, **kwargs)
        # customize the form dynamically.
        if job:
            if not job.require_resume:
                self.fields.pop('resume')
            if not job.require_cover_letter:
                self.fields.pop('cover_letter')
            if not job.require_portfolio:
                self.fields.pop('portfolio')
            if not job.require_github:
                self.fields.pop('github_link')



class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }

