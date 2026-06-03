# AI-Powered Resume Screening System
## Backend - Flask App

from flask import Flask, request, render_template, jsonify
import os
from werkzeug.utils import secure_filename
from utils import extract_text_from_pdf, rank_resumes

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- Home Page ----------
@app.route('/')
def home():
    return render_template('index.html')

# ---------- Analyze Resumes ----------
@app.route('/analyze', methods=['POST'])
def analyze():
    job_description = request.form.get('job_description', '').strip()
    job_title = request.form.get('job_title', 'Job Position').strip()

    if not job_description:
        return render_template('index.html',
                             error='⚠️ Please enter a job description!')

    files = request.files.getlist('resumes')
    if not files or files[0].filename == '':
        return render_template('index.html',
                             error='⚠️ Please upload at least one resume!')

    resume_texts = []
    resume_names = []
    failed_files = []

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            text = extract_text_from_pdf(filepath)
            if text:
                resume_texts.append(text)
                resume_names.append(filename)
            else:
                failed_files.append(filename)

    if not resume_texts:
        return render_template('index.html',
                             error='⚠️ Could not extract text from uploaded resumes!')

    # Rank resumes
    results = rank_resumes(job_description, resume_texts, resume_names)

    return render_template('index.html',
                         results=results,
                         job_title=job_title,
                         job_description=job_description,
                         total=len(results),
                         failed=failed_files)

# ---------- API Endpoint ----------
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    return jsonify({'message': 'API working!'}), 200
