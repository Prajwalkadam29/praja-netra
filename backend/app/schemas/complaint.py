from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.complaint import ComplaintType, ComplaintStatus

class ComplaintBase(BaseModel):
    title: str
    description: str
    complaint_type: ComplaintType
    location: Optional[str] = None
    is_anonymous: bool = False

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    severity_score: Optional[int] = None

class ComplaintResponse(ComplaintBase):
    id: int
    status: ComplaintStatus
    severity_score: int
    filed_at: datetime
    blockchain_hash: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)