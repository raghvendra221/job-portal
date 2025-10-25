from django.urls import path
from account.views import login_view,seeker_signup_view,recruiter_signup_view,logout_view, recruiter_dashboard_view,seeker_dashboard_view,home

urlpatterns = [
    path('',home,name='home' ),
    path('login/',login_view,name='login' ),
    path('signup/seeker',seeker_signup_view,name='seeker_signup' ),
    path('signup/recruiter',recruiter_signup_view,name='recruiter_signup' ),
    path('logout/',logout_view,name='logout' ),
    path('dashboard/seeker/', seeker_dashboard_view, name='seeker-dashboard'),
    path('dashboard/recruiter/', recruiter_dashboard_view, name='recruiter-dashboard'),
]