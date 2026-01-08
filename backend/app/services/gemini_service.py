import google.generativeai as genai
from app.config import settings
from PIL import Image

genai.configure(api_key=settings.GEMINI_API_KEY)

async def analyze_evidence_image(image_path: str):
    """
    Uses Gemini 1.5 Flash to describe evidence and extract text (OCR).
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    img = Image.open(image_path)
    
    prompt = """
    Analyze this image as evidence for a corruption or civic complaint.
    1. Describe what is happening in the scene.
    2. Extract any visible text (License plates, office names, ID cards).
    3. Identify if this image represents strong evidence.
    
    Return a concise summary.
    """
    
    response = model.generate_content([prompt, img])
    return response.text