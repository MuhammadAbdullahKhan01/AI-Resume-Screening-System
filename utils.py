# utils.py - Helper Functions
## PDF Text Extraction + Resume Ranking

import pdfplumber
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- Extract Text from PDF ----------
def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
        return clean_text(text)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

# ---------- Clean Text ----------
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    return text.lower().strip()

# ---------- Rank Resumes ----------
def rank_resumes(job_description, resume_texts, resume_names):
    all_texts = [job_description] + resume_texts

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Cosine Similarity
    job_vector = tfidf_matrix[0]
    resume_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(job_vector, resume_vectors)[0]

    # Build results
    results = []
    for i, (name, score) in enumerate(zip(resume_names, similarities)):
        match_percent = round(score * 100, 2)

        if match_percent >= 70:
            status = "Excellent Match"
            badge = "excellent"
        elif match_percent >= 50:
            status = "Good Match"
            badge = "good"
        elif match_percent >= 30:
            status = "Average Match"
            badge = "average"
        else:
            status = "Poor Match"
            badge = "poor"

        results.append({
            'rank': i + 1,
            'name': name.replace('.pdf', ''),
            'score': match_percent,
            'status': status,
            'badge': badge
        })

    # Sort highest score first
    results = sorted(results, key=lambda x: x['score'], reverse=True)

    # Update ranks after sorting
    for i, r in enumerate(results):
        r['rank'] = i + 1

    return results