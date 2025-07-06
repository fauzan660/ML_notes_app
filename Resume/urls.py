"""
URL configuration for Resume project.

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
from notes.views import upload_file
from job.views import upload_job
from home.views import home
from notes.views import resume_details, transformer_test
from resume_analysis.views import resume_dashboard
urlpatterns = [
    path('admin/', admin.site.urls),
    path('rank-resume/', upload_file),
    path('job/', upload_job),
    path('', home), 
    path('rank-resume/job/<int:id>/', resume_details, name='resume_detail'),
    path('rank-resume/job/<int:job_id>/resume/<int:res_id>/', resume_dashboard, name='resume_dashboard'),
    path('accounts/', include('allauth.urls')),
    path('transformer/job/<int:id>/', transformer_test)
]
