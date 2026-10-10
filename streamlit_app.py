import io
import json
import time
from xml.sax.saxutils import escape

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.agents.candidate_evaluation import evaluate_candidate
from app.agents.jd_extractor import extract_jd_data
from app.parsepdf import parse_pdf

st.set_page_config(page_title="AI Resume Screener", layout="wide")


def make_pdf(df) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20,
    )
    styles = getSampleStyleSheet()
    cell = styles["BodyText"]
    cell.fontSize = 8
    cell.leading = 10

    df = df.fillna("")
    rows = [[Paragraph(f"<b>{escape(str(c))}</b>", cell) for c in df.columns]]
    for _, row in df.iterrows():
        rows.append([Paragraph(escape(str(v)), cell) for v in row])

    widths = [35, 110, 50, 75, 150, 150, 232]
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    doc.build([Paragraph("Ranked Shortlist", styles["Title"]), Spacer(1, 10), table])
    return buffer.getvalue()


st.title("AI-Powered Resume Screening App")

st.header("1. Job Description")
jd_text = st.text_area("Paste the job description here", height=200)
jd_file = st.file_uploader("Or upload the JD (PDF)", type="pdf", key="jd")

st.header("2. Resumes")
resumes = st.file_uploader(
    "Upload resumes (PDF), you can select multiple",
    type="pdf",
    accept_multiple_files=True,
    key="multi",
)

if st.button("Rank Candidates"):
    if not resumes:
        st.warning("Upload at least one resume.")
    elif jd_file is None and not jd_text.strip():
        st.warning("Paste the JD text or upload the JD PDF first.")
    else:
        try:
            with st.spinner("Reading the job description..."):
                jd_raw = parse_pdf(jd_file) if jd_file is not None else jd_text
                jd_details = extract_jd_data(jd_raw)
                jd_json = json.dumps(jd_details)

            ranked, failed = [], []
            progress = st.progress(0.0)
            for i, r in enumerate(resumes):
                if i > 0:
                    time.sleep(5)  # stay under the per-minute limit
                try:
                    text = parse_pdf(r)
                    ev = evaluate_candidate(text, jd_json)
                    ranked.append({
                        "file": r.name,
                        "match_score": int(ev.get("match_score") or 0),
                        "recommendation": ev.get("recommendation"),
                        "matched_skills": ", ".join(ev.get("matched_skills") or []),
                        "missing_skills": ", ".join(ev.get("missing_skills") or []),
                        "summary": ev.get("summary"),
                    })
                except Exception as e:
                    failed.append({"file": r.name, "error": f"{type(e).__name__}: {e}"})
                progress.progress((i + 1) / len(resumes))

            ranked.sort(key=lambda x: x["match_score"], reverse=True)

            if ranked:
                df = pd.DataFrame(ranked)
                df.insert(0, "rank", range(1, len(df) + 1))
                st.subheader("Ranked shortlist")
                st.dataframe(df, use_container_width=True)
                st.download_button(
                    "Download shortlist PDF",
                    make_pdf(df),
                    file_name="shortlist.pdf",
                    mime="application/pdf",
                )
            for item in failed:
                st.error(f"{item['file']}: {item['error']}")
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")