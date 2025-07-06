from django.shortcuts import render
from .spacy_resume.spacy_ner import spacy_ner
from notes.models import UploadedFiles
# Create your views here.
def resume_dashboard(request, job_id, res_id):
    if request.method == "GET":
        entity = UploadedFiles.objects.get(user = request.user, pk = res_id)
        text = entity.extracted_text
        ner_results = spacy_ner(text)
        return render(request, "analysis_dashboard.html", {'job_number': job_id,'res_number': res_id, 'resume_content': text, "ner_list": ner_results })