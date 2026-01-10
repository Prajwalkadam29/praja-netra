from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.complaint import Complaint
from app.models.department import Department
from app.models.user import User  # FIXED: Added this import
from app.api.deps import require_official

router = APIRouter()


@router.get("/stats/summary")
async def get_system_stats(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_official)  # Now Python knows what User is
):
    """Returns data for Pie Charts and Top-level stats."""

    # 1. Complaints by Department (Pie Chart Data)
    dept_query = await db.execute(
        select(Department.name, func.count(Complaint.id))
        .join(Complaint, Complaint.department_id == Department.id)
        .group_by(Department.name)
    )
    dept_distribution = {name: count for name, count in dept_query.all()}

    # 2. Complaints by Status (Bar Chart Data)
    status_query = await db.execute(
        select(Complaint.status, func.count(Complaint.id))
        .group_by(Complaint.status)
    )
    # status.value is used because status is an Enum
    status_distribution = {status.value: count for status, count in status_query.all()}

    return {
        "department_pie": dept_distribution,
        "status_bar": status_distribution,
        "total_active": sum(status_distribution.values())
    }


@router.get("/map-data")
async def get_map_points(db: AsyncSession = Depends(get_db)):
    """Simplified data for the Severity Heatmap."""
    result = await db.execute(
        select(Complaint.id, Complaint.location, Complaint.severity_score, Complaint.complaint_type)
        .filter(Complaint.is_deleted == False)
    )

    return [
        {
            "id": r.id,
            "loc": r.location,
            "severity": r.severity_score,
            "type": r.complaint_type
        } for r in result.all()
    ]