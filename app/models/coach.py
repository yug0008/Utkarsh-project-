
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class CoachNote(Base):
    __tablename__ = "coach_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey("users.id"))
    athlete_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    recommendations = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    coach = relationship("User", foreign_keys=[coach_id], back_populates="coach_notes")
    athlete = relationship("User", foreign_keys=[athlete_id], back_populates="coach_notes")
