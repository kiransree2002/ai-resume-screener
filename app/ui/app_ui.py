import io
from xml.sax.saxutils import escape

import pandas as pd
import requests
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BACKEND = "http://127.0.0.1:8000"


def make_pdf(df) -> bytes:
    """Build a PDF table from the ranked shortlist DataFrame."""
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

    # columns: rank, file, match_score, recommendation, matched_skills, missing_skills, summary
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

# ---------- Job Description ----------
st.header("1. Job Description")
jd_text = st.text_area("Paste the job description here", height=200)
jd_file = st.file_uploader("Or upload the JD (PDF)", type="pdf", key="jd")

# ---------- Resumes ----------
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
        files = [("resumes", (f.name, f.getvalue(), "application/pdf")) for f in resumes]
        data = {}
        if jd_file is not None:
            files.append(("jd_file", (jd_file.name, jd_file.getvalue(), "application/pdf")))
        else:
            data["jd_text"] = jd_text

        with st.spinner(f"Ranking {len(resumes)} resumes... this can take a while"):
            response = requests.post(f"{BACKEND}/rank/", files=files, data=data, timeout=900)

        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                st.error(f"{result['error']}: {result['message']}")
            else:
                if result["ranked"]:
                    df = pd.DataFrame(result["ranked"])
                    df.insert(0, "rank", range(1, len(df) + 1))
                    st.subheader("Ranked shortlist")
                    st.dataframe(df, use_container_width=True)
                    st.download_button(
                        "Download shortlist PDF",
                        make_pdf(df),
                        file_name="shortlist.pdf",
                        mime="application/pdf",
                    )
                for item in result["failed"]:
                    st.error(f"{item['file']}: {item['error']}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")