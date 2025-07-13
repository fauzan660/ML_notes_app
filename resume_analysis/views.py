from django.shortcuts import render
from .spacy_resume.spacy_ner import spacy_ner
from notes.models import UploadedFiles
from .pdf_highlight.skill_highlight import pdf_highlight
from django.conf import settings
import os
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
        text = file.extracted_text
        ner_results = file.extracted_resume_skills
        simple_pdf_path = file.file_field.path  ## gives absolute path
        simple_pdf_url_absolute = pdf_highlight(simple_pdf_path, ner_results)
        simple_pdf_url_relative = absolute_to_media_url(simple_pdf_url_absolute)
        print(file.file_field.url)
        return render(request, "analysis_dashboard.html", {'job_number': job_id,'res_number': res_id, 'resume_content': text, "ner_list": ner_results , "pdf_file": file.file_field, "simple_pdf_url": simple_pdf_url_relative})