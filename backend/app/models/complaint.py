import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from app.database import Base

class ComplaintType(str, enum.Enum):
    BRIBERY = "bribery"
    NEPOTISM = "nepotism"
    FRAUD = "fraud"
    EMBEZZLEMENT = "embezzlement"
    OTHERS = "others"

class ComplaintStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=True)   # AI Translated Title
    summary_en = Column(Text, nullable=True)         # AI Translated Summary
    description = Column(Text)
    complaint_type = Column(Enum(ComplaintType), nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.SUBMITTED)
    severity_score = Column(Integer, default=1)
    location = Column(String(255))
    filed_at = Column(DateTime(timezone=True), server_default=func.now())
    blockchain_hash = Column(String(255), nullable=True)
    is_anonymous = Column(Boolean, default=False)
    
    # department_id will be linked once we create the department model
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    analysis_status = Column(String(20), default="pending") # pending, processing, completed, failed
    cluster_id = Column(Integer, ForeignKey("case_clusters.id"), nullable=True)

    is_deleted = Column(Boolean, default=False)