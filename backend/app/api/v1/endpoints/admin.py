from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.audit_service import audit_service
from app.api.deps import require_admin  # Import our RBAC gatekeeper
from app.models.user import User

router = APIRouter()

@router.get("/system-audit")
async def run_full_system_audit(
    db: AsyncSession = Depends(get_db),
    # This single line secures the entire endpoint for SUPER_ADMIN only
    current_admin: User = Depends(require_admin)
):
    """
    The Anti-Corruption 'Watchdog' Endpoint:
    Only accessible by Super Admins.
    Compares Blockchain events vs Database rows to find illegal deletions.
    """
    return await audit_service.run_integrity_audit(db)