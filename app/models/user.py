
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class UserRole(enum.Enum):
    ATHLETE = "athlete"
    COACH = "coach"
    ADMIN = "admin"

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    gender = Column(Enum(Gender))
    location = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    
    athlete_profile = relationship("AthleteProfile", back_populates="user", uselist=False, cascade="all, delete")
    coach_notes = relationship("CoachNote", back_populates="coach")
    performances = relationship("PerformanceData", back_populates="athlete")
    challenges_created = relationship("Challenge", back_populates="created_by")
