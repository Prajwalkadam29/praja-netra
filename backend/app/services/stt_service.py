import os
from groq import Groq
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class STTService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    async def transcribe_audio(self, file_path: str):
        """
        Transcribes audio using Groq's Whisper-large-v3.
        Supports Marathi, Hindi, and English automatically.
        """
        try:
            with open(file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(file_path), file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                    language=None, # Auto-detect language
                    temperature=0.0
                )
            return transcription.text
        except Exception as e:
            logger.error(f"STT Error: {e}")
            return None

stt_service = STTService()