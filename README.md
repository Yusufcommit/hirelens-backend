# HireLens AI — Backend

> FastAPI backend powering HireLens AI — AI-powered resume screening, TF-IDF similarity scoring, and candidate ranking.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi&logoColor=white)
![Deployed on Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=flat&logo=render&logoColor=white)

**Live API:** https://hirelens-backend-s2sg.onrender.com  
**Frontend Repo:** [hirelens-ai](https://github.com/Yusufcommit/hirelens-ai)  
**API Docs:** https://hirelens-backend-s2sg.onrender.com/docs

---

## What It Does

Receives resumes (PDF/DOCX) and a job description, extracts text, performs TF-IDF similarity scoring, detects missing skills, and returns a ranked list of candidates with explainable scores.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/screen` | Screen and rank candidates |

### `POST /screen`

**Request** — multipart/form-data:
- `resumes` — one or more PDF/DOCX files
- `job_description` — string

**Response:**
```json
{
  "candidates": [
    {
      "name": "John Smith",
      "score": 0.87,
      "matched_skills": ["python", "fastapi", "postgresql"],
      "missing_skills": ["docker", "kubernetes"],
      "explanation": "Strong match — 87% similarity. Notable gaps: docker, kubernetes."
    }
  ],
  "total": 1
}
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python 3.11 |
| Scoring | TF-IDF Vectorization |
| Similarity | Cosine similarity via scikit-learn |
| Resume Parsing | pdfplumber + python-docx |
| Deployment | Render |

---

## Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/Yusufcommit/hirelens-backend.git
cd hirelens-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn main:app --reload
```

API runs at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

---

## Project Structure

```
hirelens-backend/
├── main.py            # FastAPI app, routes, scoring logic
├── requirements.txt
├── .python-version
├── .gitignore
└── README.md
```

---

## How The Scoring Works

```
Resume (PDF/DOCX)
      │
      ▼
Text Extraction (pdfplumber / python-docx)
      │
      ▼
TF-IDF Vectorization
      │
      ▼
Cosine Similarity vs Job Description
      │
      ▼
Skill Extraction + Gap Analysis
      │
      ▼
Ranked Candidates + Explanations
```

---

## Roadmap

- [x] PDF and DOCX resume parsing
- [x] TF-IDF similarity scoring
- [x] Skill extraction and gap detection
- [x] Score explainability
- [x] Multi-resume batch processing
- [x] Production deployment on Render
- [ ] PostgreSQL integration for session storage
- [ ] Authentication with JWT
- [ ] Docker + CI/CD pipeline
- [ ] Bias detection layer
- [ ] API versioning (`/v1/screen`)
- [ ] Upgrade to transformer-based embeddings on better infrastructure

---

## Related

- **Frontend:** [hirelens-ai](https://github.com/Yusufcommit/hirelens-ai)
- **Original prototype:** [ai-resume-screening-system](https://github.com/Yusufcommit/ai-resume-screening-system)

---

## Built by Yusuf

**Yusuf Abdirashid** — AI Full Stack Developer  
Building polished AI-powered tools for hiring and job applications.

[![GitHub](https://img.shields.io/badge/GitHub-Yusufcommit-181717?style=flat&logo=github)](https://github.com/Yusufcommit)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Yusuf_Abdirashid-0A66C2?style=flat&logo=linkedin)](https://tr.linkedin.com/in/yusuf-abdirashid)
[![Email](https://img.shields.io/badge/Email-yusufabdirashid100@gmail.com-EA4335?style=flat&logo=gmail)](mailto:yusufabdirashid100@gmail.com)