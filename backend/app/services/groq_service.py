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
    You are an expert legal assistant for the Pune Anti-Corruption Bureau.
    Analyze the following complaint text and return a valid JSON object.
    
    COMPLAINT TEXT: "{text}"

    INSTRUCTIONS:
    1. Detect the language.
    2. If the text is in Marathi, translate the summary into clear English.
    3. Categorize the complaint (e.g., bribery, nepotism, fraud, civic_issue).
    4. Rate the severity from 1 to 10 (10 being most severe/urgent).
    5. Determine if it requires immediate police/official intervention (is_urgent).

    STRICT JSON RESPONSE FORMAT:
    {{
        "category": "string",
        "severity": integer,
        "summary_en": "string",
        "detected_language": "string",
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