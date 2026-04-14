from django.urls import path
from application.views import view_applicants, update_application_status, get_unseen_notifications, mark_notifications_read
from .views import toggle_shortlist, candidate_ai_match, recruiter_dashboard_stats, recruiter_applicants_view, generate_job_description

urlpatterns = [
    # ===== NEW FEATURE =====
    path('recruiter/applicants/', recruiter_applicants_view, name='recruiter-applicants'),
    path('ajax/generate-job-description/', generate_job_description, name='generate_job_description'),
    # ===== NEW FEATURE =====
    path('view_applicants/<int:job_id>', view_applicants, name='view-applicants'),
    path('update_application_status/<int:application_id>/', update_application_status, name='update-application-status'),
    path("ajax/get-notifications/", get_unseen_notifications, name="get_notifications"),
    path("notifications/mark-read/", mark_notifications_read, name="mark_notifications_read"),

    path('ajax/shortlist/<int:application_id>/', toggle_shortlist, name='toggle_shortlist'),
    path('ajax/candidate-match/<int:application_id>/', candidate_ai_match, name='candidate_ai_match'),
    path('ajax/dashboard-stats/', recruiter_dashboard_stats, name='recruiter_dashboard_stats'),

]