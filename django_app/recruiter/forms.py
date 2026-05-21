from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected=True

class MultipleFileField(forms.FileField):

    def clean(self,data,initial=None):

        single_file_clean=super().clean

        if isinstance(data,(list,tuple)):
            result=[single_file_clean(d,initial) for d in data]

        else:
            result=[single_file_clean(data,initial)]

        return result

class ResumeUploadForm(forms.Form):

    resumes=MultipleFileField(
        widget=MultipleFileInput(attrs={"multiple":True})
    )

    jd_text=forms.CharField(
        widget=forms.Textarea
    )