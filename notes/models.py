from django.db import models
from django.contrib.auth.models import User

JOB_TYPE_CHOICES = [
    ("FT", "Full Time"),
    ("PT", "Part Time"),
    ("FR", "Free Lance"),
    ("IN", "Internship"),
]

# Create your models here.
class UploadedFiles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_field = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True, null=True)
    
    
class PostJobModel(models.Model):
    job_title = models.CharField(max_length=100)
    job_description = models.TextField(max_length=1000)
    job_type = models.CharField(max_length=3, choices=JOB_TYPE_CHOICES)