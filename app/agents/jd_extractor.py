import json

from app.llm import client, MODEL
from app.prompts import EXTRACT_JD_DETAILS


def _clean_json(text: str):
    """Remove ```json fences if the model adds them, then parse."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def extract_jd_data(jd_text: str):
    prompt = EXTRACT_JD_DETAILS.format(jd_text=jd_text)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    print("JD response from Gemini:", content)
    return _clean_json(content)