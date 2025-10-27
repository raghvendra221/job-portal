
from django.contrib import admin
from django.urls import path,include
from account.views import home
from django.conf import settings
from django.conf.urls.static import static
# from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('account/', include('account.urls')),
    path('job/', include('job.urls')),
    path('application/', include('application.urls')),
   
    # path('', TemplateView.as_view(template_name='home.html'),name='home'),#home page using generic view
    
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
