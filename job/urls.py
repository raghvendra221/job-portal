from django.urls import path
from job.views import PostJobView,recruiter_dashboard_view,edit_job,delete_job,job_detail

urlpatterns = [
    path('post/', PostJobView.as_view(), name='post_job'),
    path('job/<int:pk>/', job_detail, name='job_detail'),
    path('dashboard/recruiter/', recruiter_dashboard_view, name='recruiter-dashboard'),
    path('editjob/<int:job_id>/',edit_job,name='edit_job'),
    path('deletejob/<int:job_id>/',delete_job,name='delete_job')
   
]