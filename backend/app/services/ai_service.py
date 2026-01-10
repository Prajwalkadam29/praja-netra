from app.services.groq_service import analyze_complaint_text, groq_client # Import client
from app.services.gemini_service import analyze_evidence_image

class AIService:
    def __init__(self):
        self.groq_client = groq_client # Use the shared client

    @staticmethod
    async def triage_complaint(description: str):
        return await analyze_complaint_text(description)

    @staticmethod
    async def process_evidence(file_path: str, description: str):
        return await analyze_evidence_image(file_path, description)

    async def predict_department(self, description_en: str, departments: list):
        # We convert the list of DB objects into a string for the LLM
        dept_list_str = "\n".join([f"ID {d.id}: {d.name} ({d.description})" for d in departments])

        prompt = f"""
        Analyze this grievance report and assign it the most relevant Department ID.
        REPORT: "{description_en}"
        DEPARTMENTS:
        {dept_list_str}
        Respond ONLY with the Department ID (integer).
        """

        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            return int(response.choices[0].message.content.strip())
        except Exception:
            return None

ai_service = AIService()