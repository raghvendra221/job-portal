from django.urls import path
from account.views import login_view,seeker_signup_view,recruiter_signup_view,logout_view,home,activate_account,seeker_dashboard_view,apply_job,my_applications,mark_all_read,resend_activation_email,password_reset,password_reset_confirm,profile_view,ai_insight_view,recruiter_search_jobs,seeker_live_search
urlpatterns = [
    path('',home,name='home' ),
    path('login/',login_view,name='login' ),
    path('signup/seeker',seeker_signup_view,name='seeker_signup' ),
    path('activate/<str:uidb64>/<str:token>/',activate_account,name='activate'),
    path('signup/recruiter',recruiter_signup_view,name='recruiter_signup' ),
    path('logout/',logout_view,name='logout' ),
    path('dashboard/seeker/', seeker_dashboard_view, name='seeker-dashboard'),
    path('apply/<int:job_id>/', apply_job, name='apply_job'),
    path('dashboard/applications/', my_applications, name='my_applications'),
    path('notifications/mark_all_read/', mark_all_read, name='mark_all_read'),
    path('resend-activation/', resend_activation_email, name='resend-activation'),
    path('password_reset/',password_reset,name='password-reset'),
    path('confirm/password_reset/<str:uidb64>/<str:token>/',password_reset_confirm,name='password-reset-confirm'),
    path('profile/',profile_view,name='profile' ),
    path('insight/', ai_insight_view, name='ai_insight'),
    path("recruiter/search-jobs/", recruiter_search_jobs, name="recruiter_search_jobs"),
    path("seeker/search-jobs/", seeker_live_search, name="seeker_live_search"),

]