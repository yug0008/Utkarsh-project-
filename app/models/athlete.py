
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class AthleteProfile(Base):
    __tablename__ = "athlete_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    age = Column(Integer)
    sport = Column(String)
    performance_stats = Column(JSON, default={})  # Stores various metrics
    injury_risk = Column(Float)  # 0-1 probability
    xp_points = Column(Integer, default=0)
    
    user = relationship("User", back_populates="athlete_profile")
    performances = relationship("PerformanceData", back_populates="athlete")
    coach_notes = relationship("CoachNote", back_populates="athlete")

class PerformanceData(Base):
    __tablename__ = "performance_data"
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("users.id"))
    test_type = Column(String, nullable=False)  # e.g., "pushups", "sprints"
    raw_video_path = Column(String, nullable=False)
    processed_video_path = Column(String)  # Optional: video with pose landmarks
    ai_score = Column(Float)  # Overall performance score
    metrics = Column(JSON)  # Detailed metrics like speed, accuracy, etc.
    cheat_detected = Column(Boolean, default=False)
    feedback = Column(JSON)  # AI-generated feedback
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    athlete = relationship("User", back_populates="performances")
