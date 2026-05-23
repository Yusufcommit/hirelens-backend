from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber
import docx
import io
import re
from typing import List

app = FastAPI(title="HireLens AI API", version="1.0.0")

# Allow Next.js frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")


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
    """Best-effort name extraction from first lines of resume."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        if len(line.split()) in range(2, 5) and line[0].isupper():
            return line
    return filename.replace(".pdf", "").replace(".docx", "").replace("_", " ").title()


def extract_skills(text: str) -> List[str]:
    """Extract likely skill keywords from resume text."""
    common_skills = [
        "python", "javascript", "typescript", "react", "next.js", "node.js",
        "fastapi", "django", "flask", "postgresql", "mysql", "mongodb", "redis",
        "docker", "kubernetes", "aws", "gcp", "azure", "git", "ci/cd",
        "machine learning", "deep learning", "nlp", "sql", "rest api",
        "graphql", "tailwind", "html", "css", "java", "c++", "go", "rust",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
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

    explanation = f"{level} — {pct}% semantic similarity with the job description."
    if missing:
        top_missing = missing[:3]
        explanation += f" Notable gaps: {', '.join(top_missing)}."
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
    jd_embedding = model.encode([job_description])
    jd_skills = extract_skills(job_description)

    candidates = []

    for resume in resumes:
        file_bytes = await resume.read()
        text = extract_text(resume.filename, file_bytes)

        if not text:
            continue

        resume_embedding = model.encode([text])
        score = float(cosine_similarity(jd_embedding, resume_embedding)[0][0])

        resume_skills = extract_skills(text)
        missing_skills = find_missing_skills(resume_skills, jd_skills)
        name = extract_name(text, resume.filename)
        explanation = generate_explanation(score, missing_skills)

        candidates.append({
            "name": name,
            "score": round(score, 4),
            "matched_skills": resume_skills,
            "missing_skills": missing_skills,
            "explanation": explanation,
        })

    # Sort by score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)

    return {"candidates": candidates, "total": len(candidates)}