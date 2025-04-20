from django.shortcuts import render, redirect
from .forms import UploadJobForm
from .models import PostJobModel
from notes.views import members
# Create your views here.

def upload_job(request):
    if request.method == "POST":
        form = UploadJobForm(request.POST)
        if form.is_valid():
            instance = PostJobModel(job_title = form.cleaned_data['title'], job_description= form.cleaned_data['description'], job_type=form.cleaned_data['type'])
            instance.save()
            print("hello")
            return redirect(members)

        else:
            print(form.errors)
    else:
        form = UploadJobForm()
    return render(request, "upload_job.html", {"form": form})