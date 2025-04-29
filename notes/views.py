from django.shortcuts import HttpResponse, render
from django.http import HttpResponseRedirect
from django.template import loader
from .forms import UploadFileForm
from .utils import read_pdf
from .models import UploadedFiles
from job.models import PostJobModel
# Create your views here.
# def members(request):
#     template = loader.get_template('notes/resume.html')
#     return HttpResponse(template.render())

def upload_file(request):
    jobs = PostJobModel.objects.all()
        
    return render(request, "notes/resume.html", {"jobs":jobs})

def resume_details(request, id):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data['resume_file']
            for each in files:
                job_instance = PostJobModel.objects.get(pk=id)
                instance = UploadedFiles(user=request.user,job=job_instance, file_field=each,extracted_text=read_pdf(each))
                instance.save()
            return HttpResponseRedirect("/members/")
    else:
        form = UploadFileForm()
        job = PostJobModel.objects.get(pk = id)
    return render(request, 'notes/resume_detail.html', {'job': job, "form": form})
    