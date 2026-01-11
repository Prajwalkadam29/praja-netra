from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship # Added
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    contact_email = Column(String(100))

    # ADD THIS LINE to link back to users
    staff = relationship("User", back_populates="department")