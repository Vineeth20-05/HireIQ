from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import CandidateForm
from recruiter.utils import extract_text_from_pdf, extract_text_from_docx
from recruiter_portal.models import CandidateResume
import requests

@login_required
def candidate_home(request):

    if request.user.role != "candidate":
        return HttpResponse("Unauthorized")

    return render(
        request,
        "candidate/home.html"
    )

@login_required
def candidate_dashboard(request):

    if request.user.role != "candidate":
        return HttpResponse("Unauthorized")

    feedback=None
    interview_questions=[]

    if request.method=="POST":

        form=CandidateForm(request.POST,request.FILES)

        if form.is_valid():

            resume=request.FILES["resume"]
            jd_text=form.cleaned_data["jd_text"]

            if not jd_text.strip():
                jd_text="Software Engineer"

            extracted_text=(
                extract_text_from_pdf(resume)
                if resume.name.endswith(".pdf")
                else extract_text_from_docx(resume)
                if resume.name.endswith(".docx")
                else ""
            )

            CandidateResume.objects.filter(
                uploaded_by=request.user
            ).delete()

            CandidateResume.objects.create(
                candidate_name=request.user.username,
                resume_file=resume,
                extracted_text=extracted_text,
                uploaded_by=request.user
            )

            # MATCH API

            try:

                match_response=requests.post(
                    "http://127.0.0.1:8001/match",
                    json={
                        "candidate_name":request.user.username,
                        "resume_text":extracted_text,
                        "jd_text":jd_text,
                        "user_id":str(request.user.id),
                        "role":request.user.role
                    },
                    timeout=30
                )

                if match_response.status_code!=200:
                    print("MATCH ERROR:",match_response.text)

            except Exception as e:
                print("MATCH EXCEPTION:",e)

            # ATS FEEDBACK API

            try:

                feedback_response=requests.post(
                    "http://127.0.0.1:8001/candidate-feedback",
                    json={
                        "candidate_name":request.user.username,
                        "resume_text":extracted_text,
                        "jd_text":jd_text,
                        "user_id":str(request.user.id),
                        "role":request.user.role
                    },
                    timeout=60
                )

                if feedback_response.status_code==200:
                    feedback=feedback_response.json()
                else:
                    print("FEEDBACK ERROR:",feedback_response.text)
                    feedback=None

            except Exception as e:
                print("FEEDBACK EXCEPTION:",e)
                feedback=None

            # INTERVIEW API

            try:

                interview_response=requests.get(
                    "http://127.0.0.1:8001/interview",
                    params={
                        "query":jd_text
                    },
                    timeout=60
                )

                if interview_response.status_code==200:
                    interview_questions=interview_response.json().get(
                        "questions",
                        []
                    )
                else:
                    print("INTERVIEW ERROR:",interview_response.text)
                    interview_questions=[]

            except Exception as e:
                print("INTERVIEW EXCEPTION:",e)
                interview_questions=[]

    else:
        form=CandidateForm()

    return render(
        request,
        "candidate/dashboard.html",
        {
            "form":form,
            "feedback":feedback,
            "interview_questions":interview_questions
        }
    )