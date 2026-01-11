from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.complaint import Complaint, ComplaintStatus
from app.models.notes import InternalNote
from app.models.user import User, UserRole
from app.api.deps import get_current_user, require_official
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class StatusUpdate(BaseModel):
    status: ComplaintStatus

class NoteCreate(BaseModel):
    content: str

# 1. Update Complaint Status
@router.patch("/complaints/{complaint_id}/status")
async def update_complaint_status(
    complaint_id: int,
    status_update: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_official: User = Depends(require_official)
):
    result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
    db_complaint = result.scalar_one_or_none()

    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # FIX: Check department_id against department_id, NOT official.id
    if db_complaint.department_id != current_official.department_id:
        raise HTTPException(status_code=403, detail="You can only manage cases within your department")

    db_complaint.status = status_update.status
    await db.commit()
    return {"status": "success", "new_status": db_complaint.status}

# 2. Add Internal Collaboration Note
@router.post("/complaints/{complaint_id}/notes")
async def add_internal_note(
    complaint_id: int,
    note_in: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_official: User = Depends(require_official)
):
    """Private notes for officials to discuss evidence or investigation progress."""
    new_note = InternalNote(
        complaint_id=complaint_id,
        author_id=current_official.id,
        content=note_in.content
    )
    db.add(new_note)
    await db.commit()
    return {"status": "success", "message": "Note added internally"}

# 3. Fetch Internal Notes (Hidden from Citizens)
@router.get("/complaints/{complaint_id}/notes")
async def get_internal_notes(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
    current_official: User = Depends(require_official)
):
    result = await db.execute(
        select(InternalNote).filter(InternalNote.complaint_id == complaint_id).order_by(InternalNote.created_at.desc())
    )
    return result.scalars().all()


# FIX: Update the dependency name to match your imported name
@router.get("/complaints")
async def get_assigned_complaints(
        current_user: User = Depends(get_current_user), # Changed from get_current_active_user
        db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.OFFICIAL:
        raise HTTPException(status_code=403, detail="Not authorized")

    # This logic is now correct assuming your SQL update was successful
    query = select(Complaint).where(Complaint.department_id == current_user.department_id)
    result = await db.execute(query)
    return result.scalars().all()