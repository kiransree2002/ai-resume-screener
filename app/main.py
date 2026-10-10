import json
from app.agents.candidate_evaluation import evaluate_candidate
from typing import List, Optional

import traceback
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from app.parsepdf import parse_pdf
from app.agents.resume_extractor import extract_resume_data
from app.agents.jd_extractor import extract_jd_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/screen/")
def screening(resume: UploadFile = File(...)):
    try:
        resume_text = parse_pdf(resume.file)
        print("PDF text length:", len(resume_text))
        resume_details_extracted = extract_resume_data(resume_text)
        return {"result": resume_details_extracted}
    except Exception as e:
        traceback.print_exc()
        return {"error": type(e).__name__, "message": str(e)}


@app.post("/extract-jd/")
def extract_jd(
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
):
    try:
        if jd_file is not None:
            text = parse_pdf(jd_file.file)
        elif jd_text and jd_text.strip():
            text = jd_text
        else:
            return {"error": "NoInput", "message": "Paste the JD text or upload a PDF."}

        print("JD text length:", len(text))
        return {"result": extract_jd_data(text)}
    except Exception as e:
        traceback.print_exc()
        return {"error": type(e).__name__, "message": str(e)}



@app.post("/evaluate/")
def evaluate(
    resume: UploadFile = File(...),
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
):
    try:
        resume_text = parse_pdf(resume.file)

        if jd_file is not None:
            jd_raw = parse_pdf(jd_file.file)
        elif jd_text and jd_text.strip():
            jd_raw = jd_text
        else:
            return {"error": "NoInput", "message": "Paste the JD text or upload a PDF."}

        resume_details = extract_resume_data(resume_text)
        jd_details = extract_jd_data(jd_raw)
        evaluation = evaluate_candidate(resume_details, json.dumps(jd_details))

        return {"resume": resume_details, "jd": jd_details, "evaluation": evaluation}
    except Exception as e:
        traceback.print_exc()
        return {"error": type(e).__name__, "message": str(e)}


@app.post("/rank/")
def rank(
    resumes: List[UploadFile] = File(...),
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
):
    try:
        if jd_file is not None:
            jd_raw = parse_pdf(jd_file.file)
        elif jd_text and jd_text.strip():
            jd_raw = jd_text
        else:
            return {"error": "NoInput", "message": "Paste the JD text or upload a PDF."}

        # JD oru pravashyame extract cheyyunnu
        jd_details = extract_jd_data(jd_raw)
        jd_json = json.dumps(jd_details)

        ranked, failed = [], []
        for r in resumes:
            try:
                text = parse_pdf(r.file)
                details = text
                ev = evaluate_candidate(details, jd_json)
                ranked.append({
                    "file": r.filename,
                    "match_score": int(ev.get("match_score") or 0),
                    "recommendation": ev.get("recommendation"),
                    "matched_skills": ", ".join(ev.get("matched_skills") or []),
                    "missing_skills": ", ".join(ev.get("missing_skills") or []),
                    "summary": ev.get("summary"),
                })
            except Exception as e:
                traceback.print_exc()
                failed.append({"file": r.filename, "error": f"{type(e).__name__}: {e}"})

        ranked.sort(key=lambda x: x["match_score"], reverse=True)
        return {"jd": jd_details, "ranked": ranked, "failed": failed}
    except Exception as e:
        traceback.print_exc()
        return {"error": type(e).__name__, "message": str(e)}