from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber
import docx
import io
from typing import List

app = FastAPI(title="HireLens AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs]).strip()


def extract_text(filename: str, file_bytes: bytes) -> str:
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    return ""


def extract_name(text: str, filename: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        if len(line.split()) in range(2, 5) and line[0].isupper():
            return line
    return filename.replace(".pdf", "").replace(".docx", "").replace("_", " ").title()


def extract_skills(text: str) -> List[str]:
    common_skills = [
        "python", "javascript", "typescript", "react", "next.js", "node.js",
        "fastapi", "django", "flask", "postgresql", "mysql", "mongodb", "redis",
        "docker", "kubernetes", "aws", "gcp", "azure", "git", "ci/cd",
        "machine learning", "deep learning", "nlp", "sql", "rest api",
        "graphql", "tailwind", "html", "css", "java", "c++", "go", "rust",
        "scikit-learn", "tensorflow", "pytorch",
    ]
    text_lower = text.lower()
    return [skill for skill in common_skills if skill in text_lower]


def find_missing_skills(resume_skills: List[str], jd_skills: List[str]) -> List[str]:
    return [skill for skill in jd_skills if skill not in resume_skills]


def generate_explanation(score: float, missing: List[str]) -> str:
    pct = round(score * 100)
    if pct >= 80:
        level = "Strong match"
    elif pct >= 60:
        level = "Good match"
    elif pct >= 40:
        level = "Partial match"
    else:
        level = "Weak match"

    explanation = f"{level} — {pct}% similarity with the job description."
    if missing:
        explanation += f" Notable gaps: {', '.join(missing[:3])}."
    return explanation


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "HireLens AI API is running"}


@app.post("/screen")
async def screen_candidates(
    resumes: List[UploadFile] = File(...),
    job_description: str = Form(...),
):
    jd_skills = extract_skills(job_description)
    candidates = []
    texts = []
    meta = []

    for resume in resumes:
        file_bytes = await resume.read()
        text = extract_text(resume.filename, file_bytes)
        if not text:
            continue
        texts.append(text)
        meta.append({
            "name": extract_name(text, resume.filename),
            "skills": extract_skills(text),
        })

    if not texts:
        return {"candidates": [], "total": 0}

    # TF-IDF scoring
    vectorizer = TfidfVectorizer(stop_words="english")
    all_docs = [job_description] + texts
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    jd_vector = tfidf_matrix[0]
    resume_vectors = tfidf_matrix[1:]
    scores = cosine_similarity(jd_vector, resume_vectors)[0]

    for i, score in enumerate(scores):
        missing = find_missing_skills(meta[i]["skills"], jd_skills)
        candidates.append({
            "name": meta[i]["name"],
            "score": round(float(score), 4),
            "matched_skills": meta[i]["skills"],
            "missing_skills": missing,
            "explanation": generate_explanation(float(score), missing),
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return {"candidates": candidates, "total": len(candidates)}