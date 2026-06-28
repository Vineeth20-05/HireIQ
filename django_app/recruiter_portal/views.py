from django.shortcuts import render, get_object_or_404
from recruiter.forms import ResumeUploadForm
from recruiter.utils import extract_text_from_pdf, extract_text_from_docx
from .models import CandidateResume
import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import os

ML_API_URL = os.getenv("ML_API_URL", "http://127.0.0.1:8001")


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
    total_candidates = 0
    strong_matches = 0
    moderate_matches = 0
    weak_matches = 0

    form = ResumeUploadForm(request.POST, request.FILES) if request.method == "POST" else ResumeUploadForm()

    if request.method == "POST" and form.is_valid():

        resumes = request.FILES.getlist("resumes")
        jd_text = form.cleaned_data["jd_text"]
        shortlist_count = int(form.cleaned_data["shortlist_count"])

        CandidateResume.objects.filter(
            uploaded_by=request.user
        ).delete()

        try:

            requests.delete(
                f"{ML_API_URL}/clear-user",
                params={
                    "user_id": str(request.user.id)
                },
                timeout=30
            )

        except Exception as e:

            print("CLEAR USER ERROR:", e)

        for resume_file in resumes:

            candidate_name = resume_file.name.split(".")[0]

            extracted_text = (
                extract_text_from_pdf(resume_file)
                if resume_file.name.endswith(".pdf")
                else extract_text_from_docx(resume_file)
                if resume_file.name.endswith(".docx")
                else ""
            )

            CandidateResume.objects.create(
                candidate_name=candidate_name,
                resume_file=resume_file,
                extracted_text=extracted_text,
                uploaded_by=request.user
            )

            try:

                requests.post(
                    f"{ML_API_URL}/match",
                    json={
                        "candidate_name": candidate_name,
                        "resume_text": extracted_text,
                        "jd_text": jd_text,
                        "user_id": str(request.user.id),
                        "role": request.user.role
                    },
                    timeout=60
                )

            except Exception as e:

                print("MATCH ERROR:", e)

        try:

            ranking_response = requests.get(
                f"{ML_API_URL}/rank",
                params={
                    "jd": jd_text,
                    "user_id": str(request.user.id),
                    "limit": shortlist_count
                },
                timeout=60
            )

            rankings = ranking_response.json().get("rankings", [])

        except Exception as e:

            print("RANK ERROR:", e)
            rankings = []

        uploaded_count = len(resumes)
        shortlist_count = min(shortlist_count, uploaded_count)
        rankings = rankings[:shortlist_count]

        for candidate in rankings:

            resume = CandidateResume.objects.filter(
                candidate_name__icontains=candidate["candidate_name"]
            ).last()

            if resume:

                candidate["resume_url"] = resume.resume_file.url
                candidate["resume_id"] = resume.id

        total_candidates = len(rankings)
        strong_matches = len([c for c in rankings if c["score"] > 75])
        moderate_matches = len([c for c in rankings if 60 <= c["score"] <= 75])
        weak_matches = len([c for c in rankings if c["score"] < 60])

    return render(
        request,
        "recruiter/dashboard.html",
        {
            "form": form,
            "rankings": rankings,
            "total_candidates": total_candidates,
            "strong_matches": strong_matches,
            "moderate_matches": moderate_matches,
            "weak_matches": weak_matches
        }
    )


@login_required
def candidate_analysis(request, candidate_name):

    jd = request.GET.get("jd")

    feedback = {}

    try:

        feedback_response = requests.get(
            f"{ML_API_URL}/feedback",
            params={
                "candidate_name": candidate_name,
                "query": jd
            },
            timeout=60
        )

        if feedback_response.status_code == 200:
            feedback = feedback_response.json()

    except Exception as e:

        print("FEEDBACK ERROR:", e)

    return render(
        request,
        "recruiter/analysis.html",
        {
            "candidate_name": candidate_name,
            "feedback": feedback
        }
    )


@login_required
def interview_assistant(request):

    interview_questions = []

    if request.method == "POST":

        jd_text = request.POST.get("jd_text")

        try:

            response = requests.get(
                f"{ML_API_URL}/recruiter-interview",
                params={
                    "query": jd_text
                },
                timeout=60
            )

            if response.status_code == 200:
                interview_questions = response.json().get("questions", [])

        except Exception as e:

            print("INTERVIEW ERROR:", e)

    return render(
        request,
        "recruiter/interview_assistant.html",
        {
            "interview_questions": interview_questions
        }
    )


@login_required
def ai_hiring_assistant(request):

    candidates = []

    if request.method == "POST":

        query = request.POST.get("query")

        try:

            response = requests.get(
                f"{ML_API_URL}/rag",
                params={
                    "query": query,
                    "user_id": str(request.user.id)
                },
                timeout=60
            )

            if response.status_code == 200:
                candidates = response.json().get("top_candidates", [])
            else:
                print("RAG ERROR:", response.text)

        except Exception as e:

            print("RAG EXCEPTION:", e)

    return render(
        request,
        "recruiter/ai_assistant.html",
        {
            "candidates": candidates
        }
    )