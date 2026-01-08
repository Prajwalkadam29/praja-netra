from app.services.groq_service import analyze_complaint_text
from app.services.gemini_service import analyze_evidence_image

class AIService:
    @staticmethod
    async def triage_complaint(description: str):
        return await analyze_complaint_text(description)

    @staticmethod
    async def process_evidence(file_path: str):
        return await analyze_evidence_image(file_path)

ai_service = AIService()