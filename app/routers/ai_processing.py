
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os
from datetime import datetime
from app.services.cloud_storage import save_upload_file

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.ai_processor import AIProcessor
from app.services.file_upload import save_upload_file
from app.models.performance import PerformanceData
from app.models.user import User, UserRole

router = APIRouter(prefix="/ai", tags=["ai_processing"])
ai_processor = AIProcessor()

@router.post("/process-video/{test_type}")
async def process_video(
    test_type: str,
    video: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ATHLETE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only athletes can upload performance videos"
        )
    
    # Save uploaded video
    video_path = await save_upload_file(video, "videos")
    
    try:
        # Process video with AI
        results = ai_processor.process_video(video_path, test_type)
        
        # Save performance data to database
        performance = PerformanceData(
            athlete_id=current_user.id,
            test_type=test_type,
            raw_video_path=video_path,
            ai_score=results.get("ai_score"),
            metrics=results.get("metrics", {}),
            cheat_detected=results.get("cheat_detected", False),
            feedback=results.get("feedback", [])
        )
        
        db.add(performance)
        db.commit()
        db.refresh(performance)
        
        # Update athlete's XP points
        if results.get("ai_score", 0) > 0:
            athlete_profile = current_user.athlete_profile
            xp_earned = int(results["ai_score"] / 10)  # 1 XP per 10 score points
            athlete_profile.xp_points += xp_earned
            db.commit()
        
        return {
            "success": True,
            "performance_id": performance.id,
            "score": results.get("ai_score"),
            "repetitions": results.get("metrics", {}).get("repetitions", 0),
            "feedback": results.get("feedback", []),
            "xp_earned": xp_earned
        }
        
    except Exception as e:
        # Clean up uploaded file if processing fails
        if os.path.exists(video_path):
            os.remove(video_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video processing failed: {str(e)}"
        )

