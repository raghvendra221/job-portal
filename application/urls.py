from django.urls import path
from application.views import view_applicants

urlpatterns = [
    path('view_applicants/<int:job_id>', view_applicants, name='view-applicants'),
]