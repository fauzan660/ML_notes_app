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
# Create your views here.
# def members(request):
#     template = loader.get_template('notes/resume.html')
#     return HttpResponse(template.render())

def upload_file(request):
    jobs = PostJobModel.objects.filter(user=request.user)
    total_resume = UploadedFiles.objects.count()
    return render(request, "notes/resume.html", {"jobs":jobs, "total_count": total_resume})

@csrf_exempt
def spacy_test(request, id):
    if request.method=="POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data['resume_file']
            print(files)
            rank_dict = {}
            score = make_spacy_entities( read_pdf(files[0]))
                
            return JsonResponse(score)
        
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
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data['resume_file']
            print(f"************{id}***************")
            rank_dict = {}
            for each in files:
                job_instance = PostJobModel.objects.get(user = request.user, pk=id)
                instance = UploadedFiles(user = request.user, job=job_instance, file_field=each,extracted_text=read_pdf(each))
                
                instance.save()
                score = score_calculator(job_instance.job_description, read_pdf(each))
                # get_ner_from_39_env(each)
                rank_dict.setdefault(f"{each.name}", []).append(score)
                rank_dict[f'{each.name}'].append(instance.id)
                time.sleep(2)
                
            sorted_score = dict(sorted(rank_dict.items(), key=lambda item: item[1][0], reverse=True))
            return render(request, "notes/resume_detail.html", {'job': job_instance, "form": form, loader:False, "score": sorted_score})
    else:
        form = UploadFileForm()
        job = PostJobModel.objects.get(pk = id)            
    return render(request, 'notes/resume_detail.html', {'job': job, "form": form})
    
    