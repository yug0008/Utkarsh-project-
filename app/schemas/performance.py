
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class PerformanceBase(BaseModel):
    test_type: str

class PerformanceCreate(PerformanceBase):
    pass

class PerformanceResponse(PerformanceBase):
    id: int
    athlete_id: int
    ai_score: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None
    cheat_detected: bool
    feedback: Optional[Dict[str, Any]] = None
    timestamp: datetime
    
    class Config:
        orm_mode = True
