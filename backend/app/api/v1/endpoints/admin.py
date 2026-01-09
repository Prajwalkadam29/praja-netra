from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.audit_service import audit_service

router = APIRouter()

@router.get("/system-audit")
async def run_full_system_audit(db: AsyncSession = Depends(get_db)):
    """
    The 'Senior Dev' Anti-Corruption Check:
    Compares Blockchain events vs Database rows.
    """
    return await audit_service.run_integrity_audit(db)