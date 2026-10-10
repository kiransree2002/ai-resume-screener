EXTRACT_CANDIDATE_DETAILS = """
You are an expert in resume screening. Your task is to extract relevant details from a resume.
You will receive a resume in text format, and you need to identify key information such as:
- name (string)
- email (string)
- phone (string)
- education (string or null)
- work_experience (integer or null)
- skills (list of strings)
- certifications (list of strings)

Your response must be a valid JSON object only, with no extra text.
Use null if a value is missing.

Here is the resume text:
{resume_text}

Expected response format:
{{
"name": "John Doe",
"email": "abc@gmail.com",
"phone": "1234567890",
"education": "Bachelor of Science in Computer Science",
"work_experience": 7,
"skills": ["python", "FastAPI", "Machine Learning"],
"certifications": ["Certified Python Developer"]
}}
"""



EXTRACT_JD_DETAILS = """
You are an expert recruiter. Your task is to extract the key requirements from a job description.
You will receive the job description in text format. Identify:
- job_title (string)
- required_skills (list of strings)
- preferred_skills (list of strings)
- min_experience_years (integer or null)
- education (string or null)
- responsibilities (list of strings)

Your response must be a valid JSON object only, with no extra text.
Use null if a value is missing.

Here is the job description:
{jd_text}

Expected response format:
{{
"job_title": "Python Developer",
"required_skills": ["python", "FastAPI", "SQL"],
"preferred_skills": ["docker", "AWS"],
"min_experience_years": 3,
"education": "Bachelor's degree in Computer Science",
"responsibilities": ["Build REST APIs", "Write unit tests"]
}}
"""


CANDIDATE_EVALUATION = """
You are an expert technical recruiter. Compare the candidate's resume details with the job requirements.
Judge only skills, experience and education. Ignore name, gender, age, nationality and university prestige.

Candidate resume text:
{resume_json}

Job requirements (JSON):
{jd_json}

Your response must be a valid JSON object only, with no extra text.

Expected response format:
{{
"match_score": 75,
"matched_skills": ["python", "FastAPI"],
"missing_skills": ["docker", "AWS"],
"experience_match": "Candidate has 2 years, job needs 3",
"education_match": "Meets the requirement",
"summary": "Short 2-3 sentence explanation of the score",
"recommendation": "Shortlist"
}}

match_score is an integer from 0 to 100.
recommendation must be one of: "Shortlist", "Maybe", "Reject".
"""