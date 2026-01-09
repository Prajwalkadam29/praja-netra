import google.generativeai as genai
from app.config import settings
from PIL import Image
from exif import Image as ExifImage
import json

genai.configure(api_key=settings.GEMINI_API_KEY)

def extract_exif_data(file_path: str):
    """Extracts GPS and Timestamp from image if available."""
    try:
        with open(file_path, 'rb') as f:
            img = ExifImage(f)
        if img.has_exif:
            return {
                "lat": str(getattr(img, "gps_latitude", "")),
                "lon": str(getattr(img, "gps_longitude", "")),
                "time": str(getattr(img, "datetime_original", ""))
            }
    except:
        return None
    return None

async def analyze_evidence_image(image_path: str, description: str):
    """
    The 'Truth Engine': Analyzes image and cross-references with text description.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    img = Image.open(image_path)
    
    prompt = f"""
    Analyze this image as evidence for the following corruption complaint:
    "{description}"
    
    Return a JSON object with:
    1. is_relevant: (bool) Does the image support the complaint or is it a placeholder/unrelated?
    2. confidence_score: (int 1-10) How strong is this evidence?
    3. detected_text: (string) Any OCR text like license plates or names.
    4. remarks: (string) Short explanation of why it is or isn't relevant.

    RESPONSE FORMAT:
    {{
        "is_relevant": bool,
        "confidence_score": int,
        "detected_text": "string",
        "remarks": "string"
    }}
    """
    
    response = model.generate_content([prompt, img])
    # Cleaning the response text to ensure it's valid JSON
    clean_json = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_json)