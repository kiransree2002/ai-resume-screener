from app.llm import client, MODEL
from app.prompts import EXTRACT_CANDIDATE_DETAILS


def extract_resume_data(resume_data):
    prompt = EXTRACT_CANDIDATE_DETAILS.format(resume_text=resume_data)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    print("Response from Gemini:", content)
    return content