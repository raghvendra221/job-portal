
from django.contrib import admin
from django.urls import path,include
from account.views import home
from django.conf import settings
from django.conf.urls.static import static
from account.views import seeker_live_search
# from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('account/', include('account.urls')),
    path('job/', include('job.urls')),
    path('application/', include('application.urls')),
    path('seeker/search-jobs/', seeker_live_search, name='seeker_live_search'),
    
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
