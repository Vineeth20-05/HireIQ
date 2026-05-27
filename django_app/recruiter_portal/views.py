from django.shortcuts import render,get_object_or_404
from recruiter.forms import ResumeUploadForm
from recruiter.utils import extract_text_from_pdf, extract_text_from_docx
from .models import CandidateResume
import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def recruiter_home(request):

    if request.user.role != "recruiter":
        return HttpResponse("Unauthorized")

    return render(
        request,
        "recruiter/home.html"
    )
    
@login_required
def recruiter_dashboard(request):
    if request.user.role != "recruiter":
        return HttpResponse("Unauthorized")

    rankings = None
    total_candidates = strong_matches = moderate_matches = weak_matches = 0
    form = ResumeUploadForm(request.POST, request.FILES) if request.method == "POST" else ResumeUploadForm()

    if request.method == "POST" and form.is_valid():
        resumes = request.FILES.getlist("resumes")
        jd_text = form.cleaned_data["jd_text"]

        requests.delete("http://127.0.0.1:8001/clear")
        CandidateResume.objects.all().delete()

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
                extracted_text=extracted_text,
                uploaded_by=request.user
            )

            requests.post("http://127.0.0.1:8001/match", json={
                "candidate_name": candidate_name,
                "resume_text": extracted_text,
                "jd_text": jd_text
            })

        ranking_response = requests.get("http://127.0.0.1:8001/rank", params={"jd": jd_text})
        rankings = ranking_response.json().get("rankings")

        for candidate in rankings:
            resume = CandidateResume.objects.filter(candidate_name__icontains=candidate["candidate_name"]).last()
            if resume:
                candidate["resume_url"] = resume.resume_file.url
                candidate["resume_id"] = resume.id

        total_candidates = len(rankings)
        strong_matches = len([c for c in rankings if c["score"] > 75])
        moderate_matches = len([c for c in rankings if 60 <= c["score"] <= 75])
        weak_matches = len([c for c in rankings if c["score"] < 60])

    return render(request, "recruiter/dashboard.html", {
        "form": form,
        "rankings": rankings,
        "total_candidates": total_candidates,
        "strong_matches": strong_matches,
        "moderate_matches": moderate_matches,
        "weak_matches": weak_matches
    })

@login_required
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
            'analysis':feedback
        }
    )
    
@login_required
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
    
