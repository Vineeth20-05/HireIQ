from django import forms

class CandidateForm(forms.Form):
    resume = forms.FileField()

    jd_text = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Optional Job Description"}
        ),
        required=False
    )
