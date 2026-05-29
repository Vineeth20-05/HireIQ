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
        widget=forms.Textarea(attrs={
            "placeholder":"Paste Job Description Here"
        })
    )
    
    shortlist_count = forms.IntegerField(
    label="Candidates to Shortlist",initial=5,min_value=1,
    widget=forms.NumberInput(
        attrs={
            "class":"input input-bordered w-full",
            "placeholder":"Enter number"
        }
    )
)
    
    def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.fields['resumes'].widget.attrs.update(
                {
                    'class':'file-input file-input-bordered w-full'
                }
            )
            self.fields['jd_text'].widget.attrs.update(
                {
                    'class':'textarea textarea-bordered w-full h-40'
                }
            )