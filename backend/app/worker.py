from celery import Celery
from app.config import settings
from app.database import SessionLocal
from app.models.complaint import Complaint
from app.models.evidence import Evidence
from app.services.ai_service import ai_service
from sqlalchemy import select
import asyncio
import logging

# Configure Logging for Production visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "worker",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)


def run_async(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@celery_app.task(name="analyze_complaint_task")
def analyze_complaint_task(complaint_id: int):
    run_async(process_analysis(complaint_id))


async def process_analysis(complaint_id: int):
    async with SessionLocal() as db:
        # 1. Fetch Complaint
        result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
        db_complaint = result.scalar_one_or_none()
        if not db_complaint:
            logger.error(f"Complaint {complaint_id} not found.")
            return

        logger.info(f"🚀 Starting Multi-Factor Analysis for Complaint {complaint_id}")

        # 2. Text Analysis (Groq) - The Foundation (60% Weightage)
        full_text = f"Title: {db_complaint.title}. Description: {db_complaint.description}"
        text_analysis = await ai_service.triage_complaint(full_text)

        text_severity = float(text_analysis.get("severity", 1))
        db_complaint.title_en = text_analysis.get("translated_title_en")
        db_complaint.summary_en = text_analysis.get("summary_en")
        is_urgent_text = text_analysis.get("is_urgent", False)

        # 3. Evidence Analysis (Gemini) - The Verification (40% Weightage)
        ev_result = await db.execute(select(Evidence).filter(Evidence.complaint_id == complaint_id))
        evidences = ev_result.scalars().all()

        evidence_score_sum = 0
        evidence_count = 0
        any_relevant_evidence = False

        for ev in evidences:
            if ev.file_type == "image":
                logger.info(f"📸 Analyzing Evidence Image: {ev.file_url}")
                vision_result = await ai_service.process_evidence(ev.file_url, db_complaint.description)

                ev.is_valid_evidence = vision_result.get("is_relevant", False)
                ev.validation_remarks = vision_result.get("remarks")

                # Confidence score from Gemini (1-10)
                conf_score = float(vision_result.get("confidence_score", 1))

                if ev.is_valid_evidence:
                    # High relevance gives full weight to the confidence
                    evidence_score_sum += conf_score
                    any_relevant_evidence = True
                else:
                    # Irrelevant evidence acts as a heavy penalty (1)
                    evidence_score_sum += 1

                evidence_count += 1

        # 4. Weighted Calculation Logic
        if evidence_count > 0:
            avg_evidence_score = evidence_score_sum / evidence_count
            # Final Score = (60% Text) + (40% Evidence)
            final_score = (text_severity * 0.6) + (avg_evidence_score * 0.4)

            # Special Case: If evidence is relevant but text was vague,
            # we trust the visual proof and slightly boost.
            if any_relevant_evidence and final_score < 10:
                final_score += 0.5
        else:
            # If no evidence, the score is based purely on text but slightly conservative
            final_score = text_severity

        # 5. The Urgency Override
        if is_urgent_text:
            final_score = max(final_score, 8.5)  # Force high severity if AI flags urgency

        # 6. Final Data Updates
        db_complaint.severity_score = int(round(max(1, min(10, final_score))))
        db_complaint.analysis_status = "completed"

        await db.commit()
        logger.info(f"✅ Analysis Complete for ID {complaint_id}. Final Severity: {db_complaint.severity_score}")