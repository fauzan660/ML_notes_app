import csv
import json
from collections import defaultdict

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from notes.views import upload_file

from .forms import UploadJobForm
from .job_utils.job_gen import generate_description 
from .job_utils.job_ner import textual_ner
from .models import PostJobModel
from .utils import load_cities_by_country, load_industries

BASE_DIR = settings.BASE_DIR


@login_required
def upload_job(request):

    if request.method == "POST":
        if request.user.is_authenticated == False:
            return redirect("/accounts/google/login")
        else:
            form = UploadJobForm(request.POST)
            if form.is_valid():
                # instance = PostJobModel(user = request.user, job_title = form.cleaned_data['title'], job_description= form.cleaned_data['description'], job_type=form.cleaned_data['type'])
                # instance.extracted_skills = textual_ner(form.cleaned_data['description'])
                # instance.save()

                cleaned_data = form.cleaned_data
                job = form.save(commit=False)
                job.user = request.user
                job.save()
                print(job)
                return redirect("rank-resume")
            else:
                print(form.errors)
                return render(
                    request,
                    "job/upload_job.html",
                    {
                        "form": form,
                    },
                )
    else:
        industries = load_industries()
        cities_by_country = load_cities_by_country()
        countries = sorted(list(cities_by_country.keys()))
        form = UploadJobForm()
        return render(
            request,
            "job/upload_job.html",
            {
                "form": form,
                "industries": industries,
                "countries": json.dumps(countries),
                "cities_by_country": json.dumps(cities_by_country),
            },
        )


def generate_job_description(request):
    if request.method == "POST":
        data = json.loads(request.body)
        job_title = data.get("job_title")
        job_type = data.get("job_type")
        work_mode = data.get("work_mode")
        industry = data.get("industry")
        experience_level = data.get("experience_level")
        min_experience = data.get("min_experience")
        max_experience = data.get("max_experience")
        country = data.get("country")
        city = data.get("city")

        # Now you have all the data to use with your GenAI prompt.
        # Example dummy response:
        desc = generate_description(
            job_title=job_title,
            job_type=job_type,
            work_mode=work_mode,
            industry=industry,
            experience_level=experience_level,
            min_experience=min_experience,
            max_experience=max_experience,
            country=country,
            city=city,
        )

        return JsonResponse({"description": desc})
