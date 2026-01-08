from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.complaint import Complaint
from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from fastapi import File, UploadFile
from app.utils.file_handler import save_upload_file
from app.models.evidence import Evidence, FileType

router = APIRouter()

@router.post("/", response_model=ComplaintResponse)
async def create_complaint(
    complaint_in: ComplaintCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_complaint = Complaint(**complaint_in.model_dump())
    db.add(db_complaint)
    await db.commit()
    await db.refresh(db_complaint)
    return db_complaint

@router.get("/", response_model=List[ComplaintResponse])
async def list_complaints(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Complaint).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/{complaint_id}/evidence")
async def upload_evidence(
    complaint_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. Verify complaint exists
    result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
    if not result.scalar():
        raise HTTPException(status_code=404, detail="Complaint not found")

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
        file_url=file_path
    )
    db.add(new_evidence)
    await db.commit()
    
    return {"status": "success", "file_path": file_path}