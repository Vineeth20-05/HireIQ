from django import forms

class CandidateForm(forms.Form):
    resume = forms.FileField()

    jd_text = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Optional Job Description"}
        ),
        required=False
    )
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['resume'].widget.attrs.update(
            {
                'class':'file-input file-input-bordered w-full'
            }
        )
        self.fields['jd_text'].widget.attrs.update(
            {
                'class':'textarea textarea-bordered w-full h-40'
            }
        )