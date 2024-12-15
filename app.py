from flask import Flask, request, jsonify
import spacy
import pdfplumber  # For PDF parsing
import requests
import csv

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

# Function to load skills from a CSV file
def load_skills_from_csv(file_path):
    skills = set()
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Use the correct column name from your CSV, i.e., 'Skills'
            skills.add(row['Skills'].strip())  # Changed 'skill' to 'Skills'
    return skills

# Load skills from the CSV file
SKILLS_LIST = load_skills_from_csv('C:/Users/ASUS/OneDrive/Desktop/resumeFin/skills_dataset.csv')

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    data = request.json
    resume_url = data.get('resumeUrl')

    try:
        # Fetch and extract text from the resume
        resume_text = download_and_extract_resume(resume_url)

        # Analyze resume text with SpaCy
        doc = nlp(resume_text)

        # Extract skills
        extracted_skills = extract_skills(resume_text)
        recommendations = generate_recommendations(extracted_skills)

        return jsonify({
            "skills": extracted_skills,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def download_and_extract_resume(resume_url):
    # Download the resume from the URL
    response = requests.get(resume_url)
    if response.status_code != 200:
        raise Exception("Failed to download the resume.")

    # Save the file locally for parsing
    resume_path = "resume.pdf"
    with open(resume_path, 'wb') as f:
        f.write(response.content)

    # Extract text from PDF
    with pdfplumber.open(resume_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    if not text.strip():
        raise Exception("Failed to extract text from the resume.")

    return text

def extract_skills(resume_text):
    # Match skills from the predefined list
    found_skills = set()

    for skill in SKILLS_LIST:
        if skill.lower() in resume_text.lower():
            found_skills.add(skill)

    return list(found_skills)

def generate_recommendations(skills):
    # Advanced recommendation logic
    recommendations = []

    if "Python" in skills:
        recommendations.append("Advanced Python Programming")
    if "Machine Learning" in skills:
        recommendations.append("Deep Learning Specialization")
    if "AWS" in skills:
        recommendations.append("AWS Solutions Architect Certification")

    if not recommendations:
        recommendations.append("Explore courses to expand your skill set.")

    return recommendations

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
