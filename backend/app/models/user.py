from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey # Add ForeignKey
from sqlalchemy.orm import relationship # Add relationship
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    CITIZEN = "CITIZEN"
    OFFICIAL = "OFFICIAL"
    SUPER_ADMIN = "SUPER_ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    google_id = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN)

    # ADD THIS LINE
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    # Relationship to access department name easily
    department = relationship("Department", back_populates="staff")

    is_active = Column(Boolean, default=True)