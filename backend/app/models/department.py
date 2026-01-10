from sqlalchemy import Column, Integer, String
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False) # e.g., "PMC Road Dept"
    description = Column(String(255))
    contact_email = Column(String(100))