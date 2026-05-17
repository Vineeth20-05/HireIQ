import pdfplumber
from docx import Document

def extract_text_from_pdf(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)

    text = "\n".join([para.text for para in doc.paragraphs])

    return text