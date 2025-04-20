from django.db import models

# Create your models here.
JOB_TYPE_CHOICES = [
    ("FT", "Full Time"),
    ("PT", "Part Time"),
    ("FR", "Free Lance"),
    ("IN", "Internship"),
]

# Create your models here.
class UploadedFiles(models.Model):
    file_field = models.FileField(upload_to='resumes/')
    
    
class PostJobModel(models.Model):
    job_title = models.CharField(max_length=100)
    job_description = models.TextField(max_length=1000)
    job_type = models.CharField(max_length=3, choices=JOB_TYPE_CHOICES)