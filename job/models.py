

from django.db import models
from authentication.models import CustomUser
from django.db.models import JSONField  # Django 3.1+
# Create your models here.
JOB_TYPE_CHOICES = [
    ('Full-time', 'Full-time'),
    ('Part-time', 'Part-time'),
    ('Contract', 'Contract'),
    ('Internship', 'Internship'),
]

WORK_MODE_CHOICES = [
    ('On-site', 'On-site'),
    ('Remote', 'Remote'),
    ('Hybrid', 'Hybrid'),
]

EXPERIENCE_LEVEL_CHOICES = [
    ('Entry-Level', 'Entry-Level'),
    ('Mid-Level', 'Mid-Level'),
    ('Senior-Level', 'Senior-Level'),
]
# Create your models here.
    
    

class PostJobModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)
    job_description = models.TextField(max_length=1000)
    job_type = models.CharField(max_length=10, choices=JOB_TYPE_CHOICES)
    extracted_skills = JSONField(default=list)  # Stores lists/dicts natively
    work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, blank=True, null=True)
    industry = models.CharField(max_length=255)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, blank=True, null=True)
    min_experience = models.PositiveIntegerField(blank=True, null=True)
    max_experience = models.PositiveIntegerField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} ({self.user.username})"

    def get_job_resume(self):
        count = self.resume_files.count()
        return count

    def total_resume_count(self):
        from notes.models import UploadedFiles
        job_count = self.get_job_resume()
        total_count = UploadedFiles.objects.count()
        return int((job_count / total_count) * 100) if total_count != 0 else 0
