from django import forms
from .models import Resume

class ResumeUploadForm(forms.ModelForm):
    jd_text = forms.CharField(
        widget=forms.Textarea
    )

    class Meta:
        model = Resume
        fields = ['name', 'resume_file']