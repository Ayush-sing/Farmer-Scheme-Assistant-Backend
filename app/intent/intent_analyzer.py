from groq import Groq
from app.intent.prompts import INTENT_ANALYSIS_PROMPT
from app.intent.prompts import CLARIFICATION_PROMPT
from app.core.config import LLM_API_KEY, LLM_MODEL_NAME
import json
import re

client = Groq(api_key=LLM_API_KEY)

def normalize_user_message(text: str) -> str:
    if not text:
        return ""
    # keep meaning but remove weird spacing + too many newlines
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)          # max 2 newlines
    text = re.sub(r"[ \t]{2,}", " ", text)          # collapse spaces
    return text.strip()

def analyze_intent(user_message: str) -> dict:
    
    user_message = normalize_user_message(user_message)
    prompt = INTENT_ANALYSIS_PROMPT + user_message

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    raw_output = response.choices[0].message.content

    try:
        return json.loads(raw_output)
    except Exception:
        # Safety fallback (LLM output guard)
        return {
            "intent_summary": "Unable to clearly understand the request",
            "extracted_details": {},
            "clarity": "unclear",
            "missing_information": ["rephrase request"]
        }

def generate_clarification(missing_info: list) -> str:
    prompt = CLARIFICATION_PROMPT + ", ".join(missing_info)

    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
