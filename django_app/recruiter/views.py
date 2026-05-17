from django.shortcuts import render, redirect
from .forms import ResumeUploadForm
from .utils import extract_text_from_pdf, extract_text_from_docx

def home(request):
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

            return redirect('home')

    else:
        form = ResumeUploadForm()

    return render(request, 'home.html', {'form': form})