from django.shortcuts import HttpResponse, render
from django.http import HttpResponseRedirect
from django.template import loader
from .forms import UploadFileForm
from .utils import read_pdf
from .models import UploadedFiles
# Create your views here.
# def members(request):
#     template = loader.get_template('notes/resume.html')
#     return HttpResponse(template.render())

def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data['resume_file']
            for each in files:
                instance = UploadedFiles(file_field=each)
                read_pdf(each)
                instance.save()
            return HttpResponseRedirect("/members/")
    else:
        form = UploadFileForm()
        
    return render(request, "notes/resume.html", {"form": form})
