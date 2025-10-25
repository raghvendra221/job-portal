from django.urls import path
from job.views import PostJobView,recruiter_dashboard_view

urlpatterns = [
    path('post/', PostJobView.as_view(), name='post_job'),
    path('dashboard/recruiter/', recruiter_dashboard_view, name='recruiter-dashboard'),
]