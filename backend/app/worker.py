from celery import Celery
from app.config import settings
from app.database import SessionLocal
from app.models.complaint import Complaint
from app.models.evidence import Evidence
from app.models.cluster import CaseCluster
from app.models.department import Department
from app.services.ai_service import ai_service
from app.services.gemini_service import extract_exif_data
from app.services.embedding_service import embedding_service
from app.services.blockchain_service import blockchain_service
from sqlalchemy import select, update, func
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

        logger.info(f"🚀 Starting Intelligence Orchestration for ID: {complaint_id}")

        # 2. Multilingual Text Analysis (Groq) - 60% Weight
        full_text = f"Title: {db_complaint.title}. Description: {db_complaint.description}"
        text_analysis = await ai_service.triage_complaint(full_text)

        base_severity = float(text_analysis.get("severity", 1))
        db_complaint.title_en = text_analysis.get("translated_title_en")
        db_complaint.summary_en = text_analysis.get("summary_en")
        is_urgent_text = text_analysis.get("is_urgent", False)

        # 3. Evidence & Metadata Verification - 40% Weight
        ev_result = await db.execute(select(Evidence).filter(Evidence.complaint_id == complaint_id))
        evidences = ev_result.scalars().all()

        evidence_score_sum = 0
        evidence_count = 0

        for ev in evidences:
            if ev.file_type == "image":
                # Metadata extraction
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
                                metadata_penalty = 3.0  # Stale evidence penalty
                        except:
                            pass

                # Vision Truth Engine
                vision_result = await ai_service.process_evidence(ev.file_url, db_complaint.description)
                ev.is_valid_evidence = vision_result.get("is_relevant", False)
                ev.validation_remarks = vision_result.get("remarks", "")

                conf_score = float(vision_result.get("confidence_score", 1))
                if ev.is_valid_evidence:
                    evidence_score_sum += max(1, conf_score - metadata_penalty)
                else:
                    evidence_score_sum += 1  # Base score for irrelevant/spam
                evidence_count += 1

        # 4. Final Base Score Calculation
        if evidence_count > 0:
            avg_evidence_score = evidence_score_sum / evidence_count
            final_score = (base_severity * 0.6) + (avg_evidence_score * 0.4)
        else:
            final_score = base_severity

        # 5. VECTOR DB: INDEXING & REFINED CASE CLUSTERING
        analysis_txt = db_complaint.summary_en or db_complaint.description
        current_loc_parts = set(str(db_complaint.location).lower().replace(',', '').split())

        # A. Indexing
        await embedding_service.index_complaint(
            complaint_id=db_complaint.id,
            text=analysis_txt,
            metadata={"location": str(db_complaint.location), "category": text_analysis.get("category")}
        )

        # B. Finding Matches
        similar_cases = await embedding_service.find_similar_cases(analysis_txt, distance_threshold=0.45)

        # C. SPATIAL FILTER: Handles variations like "Baner" vs "Baner, Pune"
        local_matches = []
        for c in similar_cases:
            match_loc_parts = set(str(c['metadata'].get('location', '')).lower().replace(',', '').split())
            if current_loc_parts & match_loc_parts:  # Intersection check
                local_matches.append(c)

        # D. CLUSTERING & BACK-LINKING
        if len(local_matches) >= 2:
            logger.warning(f"⚠️ SYSTEMIC CLUSTER IDENTIFIED IN {db_complaint.location}")

            # Feature 3: Sliding Scale Boost
            avg_dist = sum(c['distance'] for c in local_matches) / len(local_matches)
            density_boost = len(local_matches) * (1.0 - avg_dist)
            final_score += min(3.0, density_boost)

            # Feature 2: Persistent Back-linking & Group Management
            match_ids = [int(m['id']) for m in local_matches]

            # Check if anyone in this group already belongs to a cluster
            res = await db.execute(
                select(Complaint.cluster_id).filter(Complaint.id.in_(match_ids), Complaint.cluster_id != None))
            existing_cluster_id = res.scalar()

            if existing_cluster_id:
                # Add current to existing file
                db_complaint.cluster_id = existing_cluster_id
                # Atomic Count Update: Count all linked to this cluster + this new one
                res_count = await db.execute(
                    select(func.count(Complaint.id)).filter(Complaint.cluster_id == existing_cluster_id))
                actual_total = (res_count.scalar() or 0) + 1
                await db.execute(update(CaseCluster).where(CaseCluster.id == existing_cluster_id).values(
                    complaint_count=actual_total))
            else:
                # Create NEW Cluster and link ALL existing matches to it
                new_cluster = CaseCluster(
                    cluster_name=f"Hotspot: {db_complaint.location} - {text_analysis.get('category', 'General')}",
                    category=text_analysis.get("category"),
                    location_zone=db_complaint.location,
                    avg_severity=int(final_score),
                    complaint_count=len(match_ids)
                )
                db.add(new_cluster)
                await db.flush()  # Secure the ID

                # CRITICAL: BACK-LINK PREVIOUS COMPLAINTS (Ensures ID 1 gets the ID too)
                await db.execute(
                    update(Complaint)
                    .where(Complaint.id.in_(match_ids))
                    .values(cluster_id=new_cluster.id)
                )
                db_complaint.cluster_id = new_cluster.id

        # 🚀 NEW: MODULE 8 - DEPARTMENT AUTO-ASSIGNMENT
        logger.info(f"📂 Categorizing Department for ID {complaint_id}...")

        # 1. Fetch all available departments
        dept_result = await db.execute(select(Department))
        all_departments = dept_result.scalars().all()

        # 2. Ask AI to pick the best ID
        assigned_dept_id = await ai_service.predict_department(
            description_en=db_complaint.summary_en or db_complaint.description,
            departments=all_departments
        )

        if assigned_dept_id:
            db_complaint.department_id = assigned_dept_id
            logger.info(f"📍 Automatically assigned to Department ID: {assigned_dept_id}")

        # 6. Persistence & Final Triage
        if is_urgent_text: final_score = max(final_score, 8.5)
        db_complaint.severity_score = int(round(max(1, min(10, final_score))))
        db_complaint.analysis_status = "completed"

        # 7. BLOCKCHAIN ANCHORING (Feature: Immutable Proof of Stake)
        evidence_hashes = [ev.file_hash for ev in evidences if ev.file_hash]

        manifest_hash = blockchain_service.generate_manifest_hash(
            complaint_data={
                "id": db_complaint.id,
                "description": db_complaint.description,
                "severity": db_complaint.severity_score,
                "filed_at": db_complaint.filed_at
            },
            evidence_hashes=evidence_hashes
        )

        logger.info(f"🔗 Anchoring Manifest to Blockchain for ID {complaint_id}...")
        tx_id = await blockchain_service.anchor_to_blockchain(db_complaint.id, manifest_hash)

        if tx_id:
            db_complaint.blockchain_hash = tx_id
            logger.info(f"🔒 Case Sealed! TXID: {tx_id}")

        await db.commit()
        logger.info(f"✅ Full Intelligence Loop Complete for ID {complaint_id}. Cluster ID: {db_complaint.cluster_id}")
