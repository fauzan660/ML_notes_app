from django.shortcuts import render, redirect
from .forms import UploadJobForm
from .models import PostJobModel
from notes.views import upload_file
from .job_ner import textual_ner
from django.contrib.auth.decorators import login_required
import csv
from collections import defaultdict
from django.shortcuts import render
import json
from .job_gen import generate_description
from django.http import JsonResponse

@login_required
def upload_job(request):


    if request.method == "POST":
        if request.user.is_authenticated == False:
            return redirect('/accounts/google/login')
        else:
            form = UploadJobForm(request.POST)
            if form.is_valid():
                # instance = PostJobModel(user = request.user, job_title = form.cleaned_data['title'], job_description= form.cleaned_data['description'], job_type=form.cleaned_data['type'])
                # instance.extracted_skills = textual_ner(form.cleaned_data['description'])
                # instance.save()
                    
                cleaned_data = form.cleaned_data
                job = PostJobModel.objects.create(
                    user=request.user,
                    job_title=cleaned_data['job_title'],
                    job_description=cleaned_data['job_description'],
                    job_type=cleaned_data['job_type'],
                    work_mode=cleaned_data.get('work_mode', ''),
                    industry=cleaned_data['industry'],
                    experience_level=cleaned_data.get('experience', ''),
                    min_experience=cleaned_data.get('min_experience'),
                    max_experience=cleaned_data.get('max_experience'),
                    country=cleaned_data.get('country', ''),
                    city=cleaned_data.get('city', ''),
                    extracted_skills=cleaned_data.get('extracted_skills')
                )
                print(job)
                return redirect(upload_file)
            else:
                print(form.errors)
                return render(request, "upload_job.html", {
                "form": form,
            })
    else:
   
# LIST OF INDUSTRIES
        industries = []

        with open(r'C:\Users\fauza\OneDrive\Desktop\Resume Folder\backend\Resume\job\csv_files\Industries.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            for row in reader:
                industries.append(row[0])


# LIST OF COUNTRIES AND CITIES
           # Load cities and countries from JSON
        with open(r'C:\Users\fauza\OneDrive\Desktop\Resume Folder\backend\Resume\job\json_dataset\cities_by_country.json', encoding='utf-8') as f:
            cities_by_country = json.load(f)

        countries = sorted(list(cities_by_country.keys()))
        form = UploadJobForm()
        return render(request, "upload_job.html", {
            "form": form,
            "industries": industries,
            'countries': json.dumps(countries),
            'cities_by_country': json.dumps(cities_by_country)
        })
        
def generate_job_description(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        job_title = data.get('job_title')
        job_type = data.get('job_type')
        work_mode = data.get('work_mode')
        industry = data.get('industry')
        experience_level = data.get('experience_level')
        min_experience = data.get('min_experience')
        max_experience = data.get('max_experience')
        country = data.get('country')
        city = data.get('city')

        # Now you have all the data to use with your GenAI prompt.
        # Example dummy response:
        desc = generate_description(job_title=job_title, job_type=job_type, work_mode=work_mode, industry=industry, experience_level=experience_level, min_experience=min_experience, max_experience=max_experience, country=country, city=city)

        return JsonResponse({"description": desc})
        