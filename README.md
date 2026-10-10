# AI Resume Screener

**Live demo:** https://ai-resume-ranker-app.streamlit.app/

An AI-powered tool that reads a job description and a batch of resumes (PDF), scores each candidate from 0 to 100, and produces a ranked shortlist you can download as a PDF.

## Features

- Upload or paste a **job description**
- Upload **multiple resumes** (PDF) at once
- The AI extracts the key requirements from the job description
- Each resume gets a **match score (0-100)**, matched skills, missing skills, a short summary and a recommendation (Shortlist / Maybe / Reject)
- Candidates are **ranked** from highest to lowest score
- **Download the shortlist as a PDF**
- If one resume fails, the others are still processed

## How it works

```
Job description + Resumes (PDF)
        |
        v
  PDF text extraction (pypdf)
        |
        v
  JD requirements extracted by the LLM
        |
        v
  Each resume compared with the JD by the LLM
        |
        v
  Ranked table + PDF shortlist
```

## Tech stack

- Python
- Streamlit (UI)
- Google Gemini through the OpenAI-compatible API (`openai` package)
- pypdf (PDF text extraction)
- pandas and reportlab (results table and PDF export)

## Project structure

```
ai-resume-screener/
├── streamlit_app.py        # main app
├── requirements.txt
├── .env.example
└── app/
    ├── llm.py              # LLM client and model name
    ├── parsepdf.py         # PDF to text
    ├── prompts.py          # prompts for extraction and evaluation
    └── agents/
        ├── resume_extractor.py
        ├── jd_extractor.py
        └── candidate_evaluation.py
```

## Run locally

1. Clone the repo and open the folder:
```
   git clone https://github.com/kiransree2002/ai-resume-screener.git
   cd ai-resume-screener
```
2. Create and activate a virtual environment:
```
   python -m venv venv
   venv\Scripts\activate
```
   On Mac/Linux, use `source venv/bin/activate`.
3. Install the packages:
```
   pip install -r requirements.txt
```
4. Create a `.env` file in the project root with your API key (see `.env.example`):
```
   OPEN_AI_API_KEY=your_key_here
```
5. Start the app:
```
   streamlit run streamlit_app.py
```

## Deploy

The app can be deployed on Streamlit Community Cloud. Set the main file to `streamlit_app.py` and add your key under **Secrets**:

```
OPEN_AI_API_KEY = "your_key_here"
```

## Notes

- Never commit your `.env` file or API keys. `.env` is listed in `.gitignore`.
- The free tier of the Gemini API has daily and per-minute limits, so large batches may hit rate limits.
- Scores come from an LLM's judgment, so running the same resume twice can give slightly different scores.
- Avoid uploading real candidates' resumes to a public deployment.

## Roadmap

- Skill extraction with spaCy and a TF-IDF cosine similarity baseline for comparison
- Fairness audit: demographic parity and equal opportunity metrics
- Bias alert (red/yellow/green) and a downloadable audit report
- Bias-mitigation layer for score recalibration
