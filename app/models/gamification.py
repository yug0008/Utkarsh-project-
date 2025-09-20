
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    test_type = Column(String, nullable=False)  # Type of exercise to perform
    xp_points = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"))
    deadline = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    created_by_user = relationship("User", back_populates="challenges_created")
    participations = relationship("ChallengeParticipation", back_populates="challenge")

class ChallengeParticipation(Base):
    __tablename__ = "challenge_participations"
    
    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    athlete_id = Column(Integer, ForeignKey("users.id"))
    performance_id = Column(Integer, ForeignKey("performance_data.id"))  # Link to their performance
    score = Column(Float)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    challenge = relationship("Challenge", back_populates="participations")
    athlete = relationship("User")
    performance = relationship("PerformanceData")

class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon_url = Column(String)
    criteria = Column(JSON)  # Conditions to earn this badge

class AthleteBadge(Base):
    __tablename__ = "athlete_badges"
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
