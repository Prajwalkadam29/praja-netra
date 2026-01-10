from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.database import Base

class Upvote(Base):
    __tablename__ = "upvotes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)

    # Ensure a user can only upvote a specific complaint once
    __table_args__ = (UniqueConstraint('user_id', 'complaint_id', name='_user_complaint_upvote_uc'),)