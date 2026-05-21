from django.shortcuts import render
from .forms import ResumeUploadForm
from .utils import extract_text_from_pdf,extract_text_from_docx
import requests

def home(request):
    rankings=None

    if request.method=="POST":

        form=ResumeUploadForm(request.POST,request.FILES)

        if form.is_valid():

            resumes=request.FILES.getlist("resumes")

            jd_text=form.cleaned_data["jd_text"]

            for resume_file in resumes:

                extracted_text=""

                candidate_name=resume_file.name.split(".")[0]

                if resume_file.name.endswith(".pdf"):
                    extracted_text=extract_text_from_pdf(resume_file)

                elif resume_file.name.endswith(".docx"):
                    extracted_text=extract_text_from_docx(resume_file)

                requests.post(
                    "http://127.0.0.1:8001/match",
                    json={
                        "candidate_name":candidate_name,
                        "resume_text":extracted_text,
                        "jd_text":jd_text
                    }
                )

            ranking_response=requests.get(
                "http://127.0.0.1:8001/rank",
                params={"jd":jd_text}
            )

            rankings=ranking_response.json()["rankings"]

    else:

        form=ResumeUploadForm()

    return render(
        request,
        "home.html",
        {
            "form":form,
            "rankings":rankings
        }
    )