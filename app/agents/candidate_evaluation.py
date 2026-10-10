import json

from app.llm import client, MODEL
from app.prompts import CANDIDATE_EVALUATION


def _clean_json(text: str):
    """Remove ```json fences if the model adds them, then parse."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def evaluate_candidate(candidate_details: str, jd: str):
    prompt = CANDIDATE_EVALUATION.format(resume_json=candidate_details, jd_json=jd)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    print("Evaluation response from Gemini:", content)
    return _clean_json(content)