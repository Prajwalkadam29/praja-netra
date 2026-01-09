from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class CaseCluster(Base):
    __tablename__ = "case_clusters"

    id = Column(Integer, primary_key=True, index=True)
    cluster_name = Column(String(255), nullable=False) # e.g., "Baner Water Tanker Mafia"
    category = Column(String(100))
    location_zone = Column(String(100), index=True) # The "Pune Proximity" key
    avg_severity = Column(Integer, default=1)
    complaint_count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())