from django.urls import path
from application.views import view_applicants, update_application_status

urlpatterns = [
    path('view_applicants/<int:job_id>', view_applicants, name='view-applicants'),
    path('update_application_status/<int:application_id>/', update_application_status, name='update-application-status'),
]