import os
import fitz  # PyMuPDF for PDF text extraction
import PyPDF2
import docx
import re
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ImagesForm

# Define job roles with required skills
job_roles = {
    "Data Scientist": ["Python", "Machine Learning", "SQL", "TensorFlow", "Pandas", "Numpy", "Deep Learning", "Scikit-Learn"],
    "Web Developer": ["JavaScript", "React", "Node.js", "HTML", "CSS", "Django", "Angular", "Bootstrap"],
    "Software Engineer": ["Java", "C++", "OOP", "Git", "Linux", "Spring Boot", "Microservices"],
    "Cloud Engineer": ["AWS", "Docker", "Kubernetes", "Terraform", "Azure", "GCP", "DevOps"],
    "AI Engineer": ["Artificial Intelligence", "Deep Learning", "Computer Vision", "NLP", "PyTorch", "TensorFlow"],
    "Data Analyst": ["Excel", "SQL", "Power BI", "Tableau", "Python", "Data Visualization"],
    "Cybersecurity Analyst": ["Cybersecurity", "Penetration Testing", "Networking", "Ethical Hacking", "Firewall", "Cryptography"]
}

# Extract text from PDF using PyMuPDF (fitz)
def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    extracted_text = "".join([page.get_text("text") for page in pdf_document])
    pdf_document.close()
    return extracted_text

# Extract text from DOCX using python-docx
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    return "\n".join([para.text for para in doc.paragraphs])

# Extract relevant skills from text
def extract_skills(text, skills_list):
    text = text.lower()
    return [skill for skill in skills_list if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text)]

# Find the best job role match
def match_best_role(extracted_skills):
    best_role = None
    best_matched_skills = set()
    best_match_count = 0
    unmatched_skills = None  # Fixed indentation

    for role, required_skills in job_roles.items():
        matched_skills = set(extracted_skills) & set(required_skills)
        print(f"Matched skills - {matched_skills}")

        if len(matched_skills) > best_match_count:
            best_match_count = len(matched_skills)
            best_role = role
            best_matched_skills = matched_skills

    if best_role:
        total_required_skills = len(job_roles[best_role])
        resume_score = round((best_match_count / total_required_skills) * 10)
        unmatched_skills = set(job_roles[best_role]) - best_matched_skills  # Correct calculation
    else:
        resume_score = 0
        unmatched_skills = set()

    return best_role, resume_score, unmatched_skills, best_matched_skills


# Process each resume file
def process_resume(uploaded_file):
    extracted_text = ""
    
    if uploaded_file.name.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        extracted_text = extract_text_from_docx(uploaded_file)

    if not extracted_text:
        return None

    all_possible_skills = [skill for skills in job_roles.values() for skill in skills]
    skills = extract_skills(extracted_text, all_possible_skills)
    best_role, resume_score, missing_skills , best_matched_skills= match_best_role(skills)
	
    
    return {
        "file": uploaded_file.name,
        "best_role": best_role,
        "resume_score": resume_score,
        "missing_skills": missing_skills,
        "Matched_skills":best_matched_skills
    }

# Django view function for file upload
def fileupload(request):
    form = ImagesForm()
    extracted_texts = []
    parsed_resumes = []

    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('pic')  # Allow multiple file uploads

        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.pdf') or uploaded_file.name.endswith('.docx'):
                parsed_data = process_resume(uploaded_file)

                if parsed_data:
                    parsed_resumes.append(parsed_data)

                extracted_texts.append(f"File: {uploaded_file.name}\nText Extracted Successfully!\n{'='*50}")

        if parsed_resumes:
            parsed_resumes.sort(key=lambda x: x['resume_score'], reverse=True)  # Sort resumes by score

            response_content = "<h2>Extracted Resume Data</h2><pre>"
            for result in parsed_resumes:
                response_content += (f"Resume: {result['file']}\n"
                                     f"Best Matched Role: {result['best_role']}\n"
                                     f"Resume Score: {result['resume_score']} / 10\n"
                                     f"Missing Skills : {result['missing_skills']}\n"
                                     f"Matched Skills : {result['Matched_skills']}\n"
                                     f"{'='*50}\n")
            response_content += "</pre>"
            return HttpResponse(response_content)

        return HttpResponse("No valid PDF or DOCX files uploaded.")

    context = {'form': form}
    return render(request, "upload.html", context)
