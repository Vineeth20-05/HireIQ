from django.shortcuts import render
from .forms import ResumeUploadForm
from .utils import extract_text_from_pdf, extract_text_from_docx
import requests

def home(request):
    score = None
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save()
            file_path = resume.resume_file.path
            extracted_text = ""
            if file_path.endswith('.pdf'):
                extracted_text = extract_text_from_pdf(file_path)
            elif file_path.endswith('.docx'):
                extracted_text = extract_text_from_docx(file_path)
            resume.extracted_text = extracted_text
            resume.save()
            jd_text = form.cleaned_data['jd_text']
            response = requests.post("http://127.0.0.1:8001/match", json={"candidate_name": resume.name,"resume_text": extracted_text, "jd_text": jd_text})
            result = response.json()
            score = result['match_score']
    else:
        form = ResumeUploadForm()
    return render(request, 'home.html', {'form': form, 'score': score})
