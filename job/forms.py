from django import forms 

JOB_TYPE_CHOICES = [
    ("FT", "Full Time"),
    ("PT", "Part Time"),
    ("FR", "Free Lance"),
    ("IN", "Internship"),
]

class UploadJobForm(forms.Form):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Job Title"
    }))
    description = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": 4,
        "placeholder": "Job Description"
    }))
    type = forms.ChoiceField(choices=JOB_TYPE_CHOICES, widget=forms.Select(attrs={
        "class": "form-control"
    }))
