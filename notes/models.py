from django.db import models
from django.contrib.auth.models import User
from authentication.models import CustomUser
from job.models import PostJobModel
from django.db.models import JSONField  # Django 3.1+
import uuid
JOB_TYPE_CHOICES = [
    ("FT", "Full Time"),
    ("PT", "Part Time"),
    ("FR", "Free Lance"),
    ("IN", "Internship"),
]

# Create your models here.

class UploadedFiles(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # 4 ✅ authentication url safety
    # RELATIONAL FIELDS
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default="null") # 3 ✅ authentication url safety
    job = models.ForeignKey(PostJobModel, on_delete=models.CASCADE, related_name='resume_files')

    # RESUME ORIGINAL INFO
    file_field = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True, null=True)

    # RESUME EXTRACTED INFO
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    extracted_resume_skills = JSONField(default=list)  # Stores lists/dicts natively
    college_name = models.CharField(max_length=200, blank=True, null=True)
    degree = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    total_experience = models.FloatField(
        blank=True, null=True,
        help_text="Total experience in years"
    )
    company_names = models.TextField(
    blank=True, null=True,
    help_text="Comma-separated list of company names"
    )
    
    def __str__(self):
        return self.name or "Unnamed Resume"
