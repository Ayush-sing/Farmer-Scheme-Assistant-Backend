from groq import Groq
from app.core.config import LLM_API_KEY, LLM_MODEL_NAME

client = Groq(api_key=LLM_API_KEY)

ANSWER_PROMPT = """
You are a helpful Government Schemes Assistant for Indian farmers.

You will receive:
1) user_message
2) analysis (intent_summary + extracted_details)
3) schemes_found (list of matched schemes with official links)

Your job:
- Write a clear final answer like ChatGPT.
- Show only the best 1–2 schemes from schemes_found.
- For each scheme include: Scheme name, Who can apply, Main benefit, Why it matches the user.
- Always show the official link.
- Keep it short and friendly.

Return only plain text (no JSON).
"""

def generate_answer(user_message: str, analysis: dict, schemes_found: list) -> str:
    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[
            {"role": "user", "content": ANSWER_PROMPT},
            {"role": "user", "content": f"USER_MESSAGE:\n{user_message}"},
            {"role": "user", "content": f"ANALYSIS:\n{analysis}"},
            {"role": "user", "content": f"SCHEMES_FOUND:\n{schemes_found}"}
        ],
        temperature=0.4,
        max_tokens=700
    )
    return response.choices[0].message.content.strip()
