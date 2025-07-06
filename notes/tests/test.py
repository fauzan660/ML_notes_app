# yourapp/tests/test_views.py

from django.test import TestCase, Client

class MyViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_view(self):

        if request.method == "POST":
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                files = form.cleaned_data['resume_file']
                rank_dict = {}
                for each in files:
                    job_instance = PostJobModel.objects.get(pk=id)
                    instance = UploadedFiles(user=request.user,job=job_instance, file_field=each,extracted_text=read_pdf(each))
                    instance.save()
                    score = score_calculator(job_instance.job_description, read_pdf(each))
                    get_ner_from_39_env(each)
                    rank_dict[f"{each.name}"] = score
                    time.sleep(2)
                    
                sorted_score = dict(sorted(rank_dict.items(), key=lambda item: item[1], reverse=True))
                return render(request, "notes/resume_detail.html", {'job': job_instance, "form": form, loader:False, "score": sorted_score})
        else:
            form = UploadFileForm()
            job = PostJobModel.objects.get(pk = id)            
        return render(request, 'notes/resume_detail.html', {'job': job, "form": form})
        
