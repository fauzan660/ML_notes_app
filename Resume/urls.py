from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from home.views import home
from job.views import generate_job_description, upload_job
from notes.views import resume_details, transformer_test, upload_file
from resume_analysis.views import rank_resumes_for_job, resume_dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("rank-resume/", upload_file),
    path("job/", upload_job),
    path("job/generate_description/", generate_job_description, name="ai_description"),
    path("", home),
    path("rank-resume/job/<int:id>/", resume_details, name="resume_detail"),
    path(
        "resume-analysis/<int:job_id>/<uuid:resume_uuid>/",
        rank_resumes_for_job,
        name="resume_dashboard",
    ),
    path(
        "test/job/<int:job_id>/resume/<int:res_id>/",
        rank_resumes_for_job,
        name="test_ranker",
    ),
    path("accounts/", include("allauth.urls")),
    path("transformer/job/<int:id>/", transformer_test),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
