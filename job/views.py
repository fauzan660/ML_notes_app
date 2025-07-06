from django.shortcuts import render, redirect
from .forms import UploadJobForm
from .models import PostJobModel
from notes.views import upload_file
from .job_ner import textual_ner
# Create your views here.

def upload_job(request):
    if request.method == "POST":
        if request.user.is_authenticated == False:
            return redirect('/accounts/google/login')
        else:
            form = UploadJobForm(request.POST)
            if form.is_valid():
                instance = PostJobModel(user = request.user, job_title = form.cleaned_data['title'], job_description= form.cleaned_data['description'], job_type=form.cleaned_data['type'])
                instance.extracted_skills = textual_ner(form.cleaned_data['description'])
                instance.save()
                print("hello")
                return redirect(upload_file)
            else:
                print(form.errors)
    else:
        form = UploadJobForm()
    return render(request, "upload_job.html", {"form": form})