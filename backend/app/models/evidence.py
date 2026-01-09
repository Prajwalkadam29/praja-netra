import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, Text # Added Boolean and Text
from sqlalchemy.sql import func
from app.database import Base

class FileType(str, enum.Enum):
    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"
    VIDEO = "video"

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"))
    file_type = Column(Enum(FileType), nullable=False)
    file_url = Column(String, nullable=False) # Local path or Cloud URL
    file_hash = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # New Production-Grade Columns
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    captured_at = Column(DateTime, nullable=True)
    is_valid_evidence = Column(Boolean, default=True) # For the "Truth Engine"
    validation_remarks = Column(Text, nullable=True)