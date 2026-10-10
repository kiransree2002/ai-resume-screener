import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)


def _get_key():
    key = os.getenv("OPEN_AI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets["OPEN_AI_API_KEY"]
    except Exception:
        return None


client = OpenAI(
    api_key=_get_key(),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=60,
    max_retries=1,
)

MODEL = "gemini-3.1-flash-lite"