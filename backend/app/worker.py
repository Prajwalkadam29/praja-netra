from celery import Celery
from app.config import settings
from app.database import SessionLocal
from app.models.complaint import Complaint
from app.models.evidence import Evidence
from app.services.ai_service import ai_service
from app.services.gemini_service import extract_exif_data
from app.services.embedding_service import embedding_service  # Added
from sqlalchemy import select
from datetime import datetime
import asyncio
import logging

# Configure Logging
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

        logger.info(f"🚀 Starting Multi-Factor Intelligence Loop for ID: {complaint_id}")

        # 2. Text Analysis (Groq) - 60% Weight
        full_text = f"Title: {db_complaint.title}. Description: {db_complaint.description}"
        text_analysis = await ai_service.triage_complaint(full_text)

        text_severity = float(text_analysis.get("severity", 1))
        db_complaint.title_en = text_analysis.get("translated_title_en")
        db_complaint.summary_en = text_analysis.get("summary_en")
        is_urgent_text = text_analysis.get("is_urgent", False)

        # 3. Evidence & Metadata Verification - 40% Weight
        ev_result = await db.execute(select(Evidence).filter(Evidence.complaint_id == complaint_id))
        evidences = ev_result.scalars().all()

        evidence_score_sum = 0
        evidence_count = 0
        any_relevant_evidence = False

        for ev in evidences:
            if ev.file_type == "image":
                metadata = extract_exif_data(ev.file_url)
                metadata_penalty = 0
                if metadata:
                    ev.latitude = str(metadata.get("lat"))
                    ev.longitude = str(metadata.get("lon"))
                    if metadata.get("time"):
                        try:
                            captured_dt = datetime.strptime(metadata['time'], '%Y:%m:%d %H:%M:%S')
                            ev.captured_at = captured_dt
                            if (datetime.now() - captured_dt).days > 30:
                                metadata_penalty = 3.0
                        except:
                            pass

                vision_result = await ai_service.process_evidence(ev.file_url, db_complaint.description)
                ev.is_valid_evidence = vision_result.get("is_relevant", False)
                ev.validation_remarks = vision_result.get("remarks", "")

                conf_score = float(vision_result.get("confidence_score", 1))
                if ev.is_valid_evidence:
                    evidence_score_sum += max(1, conf_score - metadata_penalty)
                    any_relevant_evidence = True
                else:
                    evidence_score_sum += 1
                evidence_count += 1

        # 4. Final Base Score Calculation
        if evidence_count > 0:
            avg_evidence_score = evidence_score_sum / evidence_count
            final_score = (text_severity * 0.6) + (avg_evidence_score * 0.4)
        else:
            final_score = text_severity

        # 5. VECTOR DB: INDEXING & PATTERN DETECTION (The Case Connector)
        # We index the translated English summary for best semantic matching
        analysis_summary = db_complaint.summary_en or db_complaint.description

        # A. Index this complaint
        await embedding_service.index_complaint(
            complaint_id=db_complaint.id,
            text=analysis_summary,
            metadata={
                "category": text_analysis.get("category"),
                "location": db_complaint.location or "Unknown"
            }
        )

        # B. Search for Clusters (Looking for systemic issues)
        similar_cases = await embedding_service.find_similar_cases(
            text=analysis_summary,
            limit=10,
            distance_threshold=0.4  # Strict threshold for corruption hotspots
        )

        # C. Corroborative Boosting
        # If > 3 similar cases exist, boost severity by 2 points
        if len(similar_cases) > 3:
            logger.warning(f"⚠️ PATTERN ALERT: Found {len(similar_cases)} similar reports. Boosting severity.")
            final_score += 2.0

        if is_urgent_text:
            final_score = max(final_score, 8.5)

        # 6. Final Data Updates
        db_complaint.severity_score = int(round(max(1, min(10, final_score))))
        db_complaint.analysis_status = "completed"

        await db.commit()
        logger.info(f"✅ Analysis Complete. Final Severity: {db_complaint.severity_score}")