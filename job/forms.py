from django import forms 
from .models import PostJobModel

# JUST TO AUTOVALIDATE THE DATA COMING FROM THE FORM IN HTML CAN BE USED TO SHOW FORM AS WELL BUT I AM NOT USING AND POST TO IT TO CHECK FIELDS AS WELL
class UploadJobForm(forms.ModelForm):
    class Meta:
        model = PostJobModel
        fields = [
            'job_title',
            'job_description',
            'job_type',
            'work_mode',
            'industry',
            'experience_level',
            'min_experience',
            'max_experience',
            'country',
            'city', 
            'extracted_skills'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Job Title"
            }),
            'job_description': forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Job Description"
            }),
            'industry': forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Industry"
            }),
            'min_experience': forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Minimum Years of Experience"
            }),
            'max_experience': forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Maximum Years of Experience"
            }),
            'country': forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Country"
            }),
            'city': forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "City"
            }),
        }