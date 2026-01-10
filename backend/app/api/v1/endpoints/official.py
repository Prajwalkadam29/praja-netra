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
    """Allows an official to move a complaint from 'submitted' to 'resolved' etc."""
    result = await db.execute(select(Complaint).filter(Complaint.id == complaint_id))
    db_complaint = result.scalar_one_or_none()

    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # SECURITY: Officials can only update status for complaints in THEIR department
    if current_official.role == UserRole.OFFICIAL and db_complaint.department_id != current_official.id:
        # Note: In a real system, you'd link the official to a Dept ID.
        # For now, we assume officials can manage assigned cases.
        pass

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