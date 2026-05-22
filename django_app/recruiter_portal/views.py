from django.shortcuts import render
from recruiter.forms import ResumeUploadForm
from recruiter.utils import extract_text_from_pdf, extract_text_from_docx
import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from recruiter.models import CandidateResume

@login_required
def recruiter_dashboard(request):
    if request.user.role!="recruiter":
        return HttpResponse("Unauthorized")
    rankings = None
    form = ResumeUploadForm(request.POST, request.FILES) if request.method == "POST" else ResumeUploadForm()

    if request.method == "POST" and form.is_valid():
        resumes = request.FILES.getlist("resumes")
        jd_text = form.cleaned_data["jd_text"]

        for resume_file in resumes:
            candidate_name = resume_file.name.split(".")[0]
            extracted_text = (
                extract_text_from_pdf(resume_file) if resume_file.name.endswith(".pdf")
                else extract_text_from_docx(resume_file) if resume_file.name.endswith(".docx")
                else ""
            )
            CandidateResume.objects.create(
            candidate_name=candidate_name,
            resume_file=resume_file,
            uploaded_by=request.user)

            requests.post("http://127.0.0.1:8001/match", json={
                "candidate_name": candidate_name,
                "resume_text": extracted_text,
                "jd_text": jd_text
            })

        ranking_response = requests.get("http://127.0.0.1:8001/rank", params={"jd": jd_text})
        rankings = ranking_response.json().get("rankings")
        for candidate in rankings:
            resume=CandidateResume.objects.filter(candidate_name=candidate["candidate_name"]).first()
            if resume:
                candidate["resume_url"]=resume.resume_file.url

    return render(request, "recruiter/dashboard.html", {"form": form, "rankings": rankings})

def candidate_analysis(request,candidate_name):
    jd=request.GET.get("jd")
    feedback_response=requests.get(
        "http://127.0.0.1:8001/feedback",
        params={
            "candidate_name":candidate_name,
            "query":jd
        }
    )
    feedback=feedback_response.json()["feedback"]
    return render(
        request,
        'recruiter/analysis.html',
        {
            'candidate_name':candidate_name,
            'feedback':feedback
        }
    )
def interview_assistant(request):
    interview_questions=None
    if request.method=="POST":
        jd_text=request.POST.get("jd_text")
        response=requests.get(
            "http://127.0.0.1:8001/recruiter-interview",
            params={"query":jd_text}
        )
        interview_questions=response.json()["interview_questions"]
    return render(
        request,
        'recruiter/interview_assistant.html',
        {
            'interview_questions':interview_questions
        }
    )