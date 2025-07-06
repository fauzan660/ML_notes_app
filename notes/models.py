from django.db import models
from django.contrib.auth.models import User
from authentication.models import CustomUser
from job.models import PostJobModel
JOB_TYPE_CHOICES = [
    ("FT", "Full Time"),
    ("PT", "Part Time"),
    ("FR", "Free Lance"),
    ("IN", "Internship"),
]

# Create your models here.

class UploadedFiles(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default="null")
    job = models.ForeignKey(PostJobModel, on_delete=models.CASCADE, related_name='resume_files')
    file_field = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True, null=True)
    
    
    