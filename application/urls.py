from django.urls import path
from application.views import view_applicants, update_application_status, get_unseen_notifications, mark_notifications_read

urlpatterns = [
    path('view_applicants/<int:job_id>', view_applicants, name='view-applicants'),
    path('update_application_status/<int:application_id>/', update_application_status, name='update-application-status'),
    path("ajax/get-notifications/", get_unseen_notifications, name="get_notifications"),
    path("notifications/mark-read/", mark_notifications_read, name="mark_notifications_read"),

]