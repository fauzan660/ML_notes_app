from django.db import models
from authentication.models import CustomUser
from django.db.models import JSONField  # Django 3.1+
# Create your models here.
JOB_TYPE_CHOICES = [
    ("FT", "Full Time"),
    ("PT", "Part Time"),
    ("FR", "Free Lance"),
    ("IN", "Internship"),
]

# Create your models here.
    
    

class PostJobModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)
    job_description = models.TextField(max_length=1000)
    job_type = models.CharField(max_length=3, choices=JOB_TYPE_CHOICES)
    extracted_skills = JSONField(default=list)  # Stores lists/dicts natively
    
    def get_job_resume(self):
        count = self.resume_files.count()
        return count

    def total_resume_count(self):
        from notes.models import UploadedFiles
        job_count = self.get_job_resume()
        total_count = UploadedFiles.objects.count()
        return int((job_count / total_count) * 100) if total_count != 0 else 0
