from django.urls import path
from application.views import view_applications

urlpatterns = [
    path('view_applications/', view_applications, name='view-applications'),
]