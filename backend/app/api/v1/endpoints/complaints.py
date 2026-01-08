from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.complaint import Complaint
from app.schemas.complaint import ComplaintCreate, ComplaintResponse

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