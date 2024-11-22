"""
URL configuration for workFlow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('HumanResource/', include('HumanResource.urls')),
    path('SignatureBusiness/', include('SignatureBusiness.urls')),
    path('R_D_Department/', include('R_D_Department.urls')),
    path('QualityAssurance/', include('QualityAssurance.urls')),
    path('Assembly/', include('Assembly.urls')),
    path('GeneralManagersOffice/', include('GeneralManagersOffice.urls')),
    path('ITInformation/', include('ITInformation.urls')),
    path('AssembleWmodel/', include('AssembleWmodel.urls')),
    path('Production_management/', include('Production_management.urls')),
    path('Packing/', include('Packing.urls')),
    path('KnowledgeDatabase/', include('KnowledgeDatabase.urls')),
    path('', include('Company.urls')),
    # path('ckeditor/upload/', CustomImageUploadView.as_view(), name='ckeditor_upload'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('schedule/', include('schedule.urls')),
    
        
] 

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)