from django.shortcuts import render
from .spacy_resume.spacy_ner import spacy_ner
from notes.models import UploadedFiles
from .pdf_highlight.skill_highlight import pdf_highlight
from django.conf import settings
from job.models import PostJobModel
import os
from .skill_compare import pred
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from .utils import rank_resume_enhanced
# Create your views here.

def absolute_to_media_url(full_path):
    # Normalize paths for cross-platform compatibility
    media_root = os.path.normpath(settings.MEDIA_ROOT)
    full_path = os.path.normpath(full_path)

    if full_path.startswith(media_root):
        # Get the relative path from media root
        relative_path = os.path.relpath(full_path, media_root)
        # Ensure URL uses forward slashes
        return f"/media/{relative_path.replace(os.sep, '/')}"
    else:
        raise ValueError("The file is not inside MEDIA_ROOT")



def resume_dashboard(request, job_id, res_id):
    if request.method == "GET":
        file = UploadedFiles.objects.get(user = request.user, pk = res_id)
        job = PostJobModel.objects.get(pk=job_id)
        job_skills = job.extracted_skills
        text = file.extracted_text
        ner_results = file.extracted_resume_skills
        print("ner hello", ner_results)
        simple_pdf_path = file.file_field.path  ## gives absolute path
        simple_pdf_url_absolute = pdf_highlight(simple_pdf_path, ner_results)
        simple_pdf_url_relative = absolute_to_media_url(simple_pdf_url_absolute)
        print(file.file_field.url)
        print("JOB", job_skills)
        resume_job_match = pred(ner_results, job_skills)
        return render(request, "analysis_dashboard.html", {'job_number': job_id,'res_number': res_id, 'resume_content': text, "ner_list": ner_results , "pdf_file": file.file_field, "simple_pdf_url": simple_pdf_url_relative, "match_data": resume_job_match})

def rank_resumes_for_job(request, job_id, resume_uuid):
    job = PostJobModel.objects.get(pk=job_id)
    resume = UploadedFiles.objects.get(user = request.user, uuid=resume_uuid) # ✅ 1 authentication url safety
    if resume.user != request.user:
        return HttpResponseForbidden("You are not allowed to view this resume.") # ✅ 2 authentication url safety
    candidate = rank_resume_enhanced(resume, job)  # Single candidate analysis
    
    context = {
        'job_company': getattr(job, 'company_name', None),
        'job_id': job_id,
        'job_title': job.job_title,
        'candidate': candidate,  # Single candidate instead of results array
    }
    return render(request, 'resume_analysis.html', context)
