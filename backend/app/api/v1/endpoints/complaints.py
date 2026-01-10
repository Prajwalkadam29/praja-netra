from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.complaint import Complaint, ComplaintType, ComplaintStatus
from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from fastapi import File, UploadFile
from app.utils.file_handler import save_upload_file, get_file_hash
from app.models.evidence import Evidence, FileType
from app.schemas.complaint import ComplaintUpdate
from app.services.ai_service import ai_service
from app.worker import analyze_complaint_task
from app.services.blockchain_service import blockchain_service
from app.services.stt_service import stt_service
from app.api.deps import get_current_user
from app.models.user import User, UserRole # Fixed Import
from app.models.social import Upvote
from sqlalchemy import func


router = APIRouter()

@router.post("/", response_model=ComplaintResponse)
async def create_complaint(
    complaint_in: ComplaintCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # PROTECTED
):
    db_complaint = Complaint(
        **complaint_in.model_dump(),
        user_id=current_user.id # Linking complaint to user
    )
    db.add(db_complaint)
    await db.commit()
    await db.refresh(db_complaint)
    return db_complaint


@router.get("/", response_model=List[ComplaintResponse])
async def list_complaints(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Added Auth
):
    # CITIZENS only see their own records. OFFICIALS see all.
    if current_user.role == UserRole.CITIZEN:
        query = select(Complaint).filter(Complaint.user_id == current_user.id, Complaint.is_deleted == False)
    else:
        query = select(Complaint).filter(Complaint.is_deleted == False)

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
        complaint_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Added Auth
):
    result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id, Complaint.is_deleted == False))
    db_complaint = result.scalar_one_or_none()

    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # SECURITY CHECK: Is the user an official or the owner?
    if current_user.role == UserRole.CITIZEN and db_complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this complaint")

    return db_complaint

@router.post("/{complaint_id}/evidence")
async def upload_evidence(
    complaint_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Added Auth
):
    # 1. Verify complaint exists
    result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
    db_complaint = result.scalar_one_or_none()

    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

        # OWNERSHIP CHECK
    if db_complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only add evidence to your own complaints")

    # 1. Generate Hash
    f_hash = await get_file_hash(file)

    # 2. FEATURE 4: Check if this file has EVER been uploaded before
    existing_ev = await db.execute(select(Evidence).filter(Evidence.file_hash == f_hash))
    if existing_ev.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Duplicate Evidence: This file has already been submitted in another report."
        )

    # 2. Save file to disk
    file_path = await save_upload_file(file)

    # 3. Determine file type
    mime_type = file.content_type
    f_type = FileType.DOCUMENT
    if "image" in mime_type: f_type = FileType.IMAGE
    elif "audio" in mime_type: f_type = FileType.AUDIO
    elif "video" in mime_type: f_type = FileType.VIDEO

    # 4. Save metadata to DB
    new_evidence = Evidence(
        complaint_id=complaint_id,
        file_type=f_type,
        file_url=file_path,
        file_hash=f_hash  # Store the hash
    )
    db.add(new_evidence)
    await db.commit()
    
    return {"status": "success", "file_path": file_path}


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
        complaint_id: int,
        complaint_update: ComplaintUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Added Auth
):
    result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
    db_complaint = result.scalar_one_or_none()

    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # SECURITY: Only owner can edit, or an Official/Admin
    if current_user.role == UserRole.CITIZEN and db_complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    update_data = complaint_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_complaint, key, value)

    await db.commit()
    await db.refresh(db_complaint)
    return db_complaint


@router.delete("/{complaint_id}")
async def delete_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Added Auth
):
    result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
    db_complaint = result.scalar_one_or_none()

    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # SECURITY: Only owner or Admin can delete
    if current_user.role == UserRole.CITIZEN and db_complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db_complaint.is_deleted = True
    await db.commit()
    return {"status": "success", "message": "Archived"}


# @router.post("/{complaint_id}/analyze")
# async def analyze_complaint(
#     complaint_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
#     db_complaint = result.scalar_one_or_none()
    
#     if not db_complaint:
#         raise HTTPException(status_code=404, detail="Complaint not found")

#     # Combine title and description for full context analysis
#     full_text = f"Title: {db_complaint.title}. Description: {db_complaint.description}"
#     ai_insights = await ai_service.triage_complaint(full_text)

#     # Store translations and scores
#     db_complaint.severity_score = ai_insights.get("severity", 1)
#     db_complaint.title_en = ai_insights.get("translated_title_en")
#     db_complaint.summary_en = ai_insights.get("summary_en")
    
#     await db.commit()
#     await db.refresh(db_complaint)
    
#     return {
#         "complaint_id": complaint_id,
#         "original_language": ai_insights.get("detected_language"),
#         "english_version": {
#             "title": db_complaint.title_en,
#             "summary": db_complaint.summary_en
#         },
#         "ai_analysis": ai_insights
#     }


@router.post("/{complaint_id}/analyze")
async def trigger_analysis(
        complaint_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Added Auth
):
    result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
    db_complaint = result.scalar_one_or_none()

    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Only owner or official can trigger
    if current_user.role == UserRole.CITIZEN and db_complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db_complaint.analysis_status = "processing"
    await db.commit()
    analyze_complaint_task.delay(complaint_id)
    
    return {
        "status": "Accepted",
        "message": "AI analysis has started in the background.",
        "complaint_id": complaint_id
    }


@router.get("/{complaint_id}/verify-integrity")
async def verify_complaint_integrity(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # FIXED: Added Auth Gate
):
    # 1. Fetch current data from SQL
    result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
    db_complaint = result.scalar_one_or_none()

    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # SECURITY: Only owner or Official can verify integrity
    if current_user.role == UserRole.CITIZEN and db_complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if not db_complaint.blockchain_hash:
        raise HTTPException(status_code=400, detail="Complaint not anchored on blockchain.")

    # 2. Get Evidence Hashes
    ev_result = await db.execute(select(Evidence).filter(Evidence.complaint_id == complaint_id))
    evidence_hashes = [ev.file_hash for ev in ev_result.scalars().all() if ev.file_hash]

    # 3. Generate a "Current" Manifest Hash
    current_hash = blockchain_service.generate_manifest_hash(
        complaint_data={
            "id": db_complaint.id,
            "description": db_complaint.description,
            "severity": db_complaint.severity_score,
            "filed_at": db_complaint.filed_at
        },
        evidence_hashes=evidence_hashes
    )

    # 4. Compare with On-Chain Data
    is_valid = await blockchain_service.verify_integrity(complaint_id, current_hash)

    return {
        "complaint_id": complaint_id,
        "is_tampered": not is_valid,
        "blockchain_tx": db_complaint.blockchain_hash,
        "status": "Verified ✅" if is_valid else "TAMPERING DETECTED ❌"
    }


@router.post("/voice-submit")
async def create_complaint_via_voice(
        location: str,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)  # PROTECTED: Requires JWT
):
    temp_path = await save_upload_file(file)
    transcript = await stt_service.transcribe_audio(temp_path)

    if not transcript:
        raise HTTPException(status_code=500, detail="Transcription failed.")

    generated_title = transcript[:50] + "..." if len(transcript) > 50 else transcript

    # Attach user_id to the voice report
    new_complaint = Complaint(
        title=f"Voice Report: {generated_title}",
        description=transcript,
        complaint_type=ComplaintType.OTHERS,
        location=location,
        status=ComplaintStatus.SUBMITTED,
        user_id=current_user.id
    )

    db.add(new_complaint)
    await db.commit()
    await db.refresh(new_complaint)

    # 5. Link audio as evidence
    f_hash = await get_file_hash(file)
    new_evidence = Evidence(
        complaint_id=new_complaint.id,
        file_type=FileType.AUDIO,
        file_url=temp_path,
        file_hash=f_hash
    )
    db.add(new_evidence)
    await db.commit()

    return {
        "status": "success",
        "complaint_id": new_complaint.id,
        "transcript": transcript
    }


@router.post("/{complaint_id}/upvote")
async def upvote_complaint(
        complaint_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Allows a citizen to upvote a complaint to increase its visibility."""
    # 1. Check if already upvoted
    existing_upvote = await db.execute(
        select(Upvote).filter(Upvote.user_id == current_user.id, Upvote.complaint_id == complaint_id)
    )
    if existing_upvote.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already upvoted this complaint")

    # 2. Add Upvote
    new_upvote = Upvote(user_id=current_user.id, complaint_id=complaint_id)
    db.add(new_upvote)

    # 3. Optional: Boost Severity score slightly on upvote (Social Severity)
    result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
    db_complaint = result.scalar_one_or_none()
    if db_complaint:
        # Every 10 upvotes, increase severity by 1 (max 10)
        db_complaint.severity_score = min(10, db_complaint.severity_score + 0.1)

    await db.commit()
    return {"status": "success", "message": "Upvoted"}


@router.get("/feed/public", response_model=List[ComplaintResponse])
async def get_public_feed(
        skip: int = 0,
        limit: int = 20,
        db: AsyncSession = Depends(get_db)
):
    """Get recent public complaints for the 'Global Feed' page."""
    # Only show complaints that are NOT anonymous and NOT deleted
    query = select(Complaint).filter(
        Complaint.is_anonymous == False,
        Complaint.is_deleted == False
    ).order_by(Complaint.filed_at.desc())

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()