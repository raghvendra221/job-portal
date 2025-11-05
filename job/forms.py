from django import forms
from application.models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'skills','description', 'location', 'salary', 'experience_required','require_resume','require_cover_letter','require_portfolio','require_github']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job title 📝'
            }),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter required skills (comma-separated) 🛠️ '
                }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter job description 📄'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter location 📍'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter salary 💰'
            }),
            'experience_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Years of experience 🕒',
                'min': 0
            }),
        }

        labels = {
            'title': 'Job Title ',
            'description': 'Job Description ',
            'location': 'Location ',
            'salary': 'Salary ',
            'experience_required': 'Experience Required ',
        }