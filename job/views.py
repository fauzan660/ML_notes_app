from django.shortcuts import render, redirect
from .forms import UploadJobForm
from .models import PostJobModel
from notes.views import upload_file
from .job_ner import textual_ner
from django.contrib.auth.decorators import login_required

def job_step_1(request):
    if request.method == "POST":
        request.session['job_title'] = request.POST.get('job_title')
        return redirect('job_step_2')
    return render(request, 'job/step1.html')

def job_step_2(request):
    if request.method == "POST":
        request.session['skills'] = request.POST.get('skills')
        return redirect('job_step_3')
    return render(request, 'job/step2.html')

def job_step_3(request):
    if request.method == "POST":
        request.session['experience'] = request.POST.get('experience')
        return redirect('job_step_4')
    return render(request, 'job/step3.html')

def job_step_4(request):
    if request.method == "POST":
        request.session['summary'] = request.POST.get('summary')
        return redirect('job_summary')
    return render(request, 'job/step4.html')

def job_summary(request):
    context = {
        'job_title': request.session.get('job_title'),
        'skills': request.session.get('skills'),
        'experience': request.session.get('experience'),
        'summary': request.session.get('summary'),
    }
    return render(request, 'job/summary.html', context)


@login_required
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