from groq import Groq
from app.config import settings
import json

client = Groq(api_key=settings.GROQ_API_KEY)

async def analyze_complaint_text(text: str):
    """
    Uses Llama-3.3-70b via Groq to analyze raw complaint text.
    Handles English and Marathi (Translation + Triage).
    """
    prompt = f"""
    You are an expert multilingual legal assistant.
    Analyze the following complaint (which may be in any language) and translate it into English for administrative review.
    
    COMPLAINT TEXT: "{text}"

    INSTRUCTIONS:
    1. Detect the primary language.
    2. Translate the TITLE of the issue into a concise English title.
    3. Translate the DESCRIPTION into a clear English summary.
    4. Categorize: bribery, nepotism, fraud, civic_issue, or harassment.
    5. Rate severity 1-10.

    STRICT JSON RESPONSE FORMAT:
    {{
        "detected_language": "string",
        "translated_title_en": "string",
        "summary_en": "string",
        "category": "string",
        "severity": integer,
        "is_urgent": boolean
    }}
    """
    
    # We are using the newer 'llama-3.3-70b-versatile' model
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )
    
    return json.loads(chat_completion.choices[0].message.content)