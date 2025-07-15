from django.contrib import admin
from django.urls import path, include
from notes.views import upload_file
from job.views import upload_job,  generate_job_description
from home.views import home
from notes.views import resume_details, transformer_test
from resume_analysis.views import resume_dashboard
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('rank-resume/', upload_file),
    path('job/', upload_job),
    path('job/generate_description/', generate_job_description, name='ai_description'),
    path('', home), 
    path('rank-resume/job/<int:id>/', resume_details, name='resume_detail'),
    path('rank-resume/job/<int:job_id>/resume/<int:res_id>/', resume_dashboard, name='resume_dashboard'),
    path('accounts/', include('allauth.urls')),
    path('transformer/job/<int:id>/', transformer_test)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
