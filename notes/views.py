from django.shortcuts import HttpResponse, render
from django.http import HttpResponseRedirect
from django.template import loader
from .forms import UploadFileForm
from .utils import read_pdf
from .models import UploadedFiles
from job.models import PostJobModel
from django.shortcuts import redirect
import time
from .transformer import transformer_similarity
from .resume_parsing import get_ner_from_39_env
from .score_calculator import score_calculator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse, HttpResponse
from resume_analysis.spacy_resume.spacy_ner import spacy_ner
from django.contrib.auth.decorators import login_required
from pyresparser import ResumeParser
import subprocess
import json
from resume_analysis.utils import rank_resume_enhanced
# Create your views here.
# def members(request):
#     template = loader.get_template('notes/resume.html')
#     return HttpResponse(template.render())

# HELPER FUNCTION
def clean_resume_skills(skills):
    if not isinstance(skills, list):
        return []
    return list(set([s.strip().lower() for s in skills if isinstance(s, str) and len(s.strip()) > 1]))

@login_required
def upload_file(request):
    jobs = PostJobModel.objects.filter(user=request.user)
    total_resume = UploadedFiles.objects.count()
    return render(request, "notes/resume.html", {"jobs":jobs, "total_count": total_resume})
        
@csrf_exempt
def transformer_test(request, id):
    if request.method=="POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data['resume_file']
            print(files)
            rank_dict = {}
            for each in files:
                job_instance = PostJobModel.objects.get(pk=id)
                instance = UploadedFiles(user=request.user,job=job_instance, file_field=each,extracted_text=read_pdf(each))
                instance.save()
                score = transformer_similarity( read_pdf(each), job_instance.job_description)
                get_ner_from_39_env(files[0])
                rank_dict[f"{each.name}"] = score
                time.sleep(2)
                
            sorted_score = dict(sorted(rank_dict.items(), key=lambda item: item[1], reverse=True))
            return render(request, "notes/resume_detail.html", {'job': job_instance, "form": form, loader:False, "score": sorted_score})


def resume_details(request, id):

    pyres_function = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\backend\Resume\notes\pyres_skill.py"
    pyres_venv = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\backend\env3.6new\Scripts\python.exe"
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data['resume_file']
            print(f"************{id}***************")
            rank_dict = {}
            job_instance = PostJobModel.objects.get(user = request.user, pk=id)
            for each in files:
                pdf_text = read_pdf(each)
                # ner_results = spacy_ner(pdf_text)
                instance = UploadedFiles(user = request.user, job=job_instance, file_field=each,extracted_text=pdf_text)
                instance.save()
                
                file_path = instance.file_field.path

                try:
                    result = subprocess.run(
                        [pyres_venv, pyres_function, file_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )

                    output = result.stdout.strip()

                    try:
                        parsed_data = json.loads(output)
                        
                    except json.JSONDecodeError:
                        parsed_data = {}
                        print("Invalid JSON from pyres_skill output")
                        print("RAW:", output)

                    # Step 4: Fill model fields with parsed data
                    instance.name = parsed_data.get("name")
                    instance.email = parsed_data.get("email")
                    instance.mobile_number = parsed_data.get("phone")
                    instance.college_name = parsed_data.get("college_name")
                    instance.degree = parsed_data.get("degree")
                    instance.designation = parsed_data.get("designation")
                    instance.total_experience = parsed_data.get("total_experience")

                    company_names = parsed_data.get("company_names", [])
                    if isinstance(company_names, list):
                        instance.company_names = ", ".join(company_names)

                    raw_skills = parsed_data.get("skills", [])
                    instance.extracted_resume_skills = clean_resume_skills(raw_skills)

                    instance.save()

                except subprocess.CalledProcessError as e:
                    print("pyres_skill failed")
                    print("STDERR:", e.stderr)


                returned_score = rank_resume_enhanced(instance, job_instance)
                print(returned_score)
                score = returned_score['final_score'] / 25
                score = round(score, 2)
                # get_ner_from_39_env(each)
                rank_dict.setdefault(f"{each.name}", []).append(score)
                rank_dict[f'{each.name}'].append(str(instance.uuid))
                time.sleep(2)
                
            sorted_score = dict(sorted(rank_dict.items(), key=lambda item: item[1][0], reverse=True))
            return render(request, "notes/resume_detail.html", {'job': job_instance, "form": form, loader:False, "score": sorted_score})
    else:
        form = UploadFileForm()
        job = PostJobModel.objects.get(pk = id, user=request.user)            
    return render(request, 'notes/resume_detail.html', {'job': job, "form": form})
    
    