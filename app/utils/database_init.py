
from app.database import engine, Base, get_db
from app.models.user import User
from app.models.athlete import AthleteProfile
from app.models.gamification import Badge, Challenge
from sqlalchemy.orm import Session
import os

def init_db():
    """Initialize database with required tables and initial data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Add initial data
    db = next(get_db())
    try:
        # Create default badges
        badges = [
            Badge(
                name="First Attempt",
                description="Complete your first assessment",
                icon_url="/badges/first-attempt.png",
                criteria={"first_assessment": True}
            ),
            Badge(
                name="Consistent Performer",
                description="Complete 5 assessments with scores above 80",
                icon_url="/badges/consistent-performer.png",
                criteria={"assessments_count": 5, "min_score": 80}
            ),
            # Add more default badges as needed
        ]
        
        for badge in badges:
            if not db.query(Badge).filter(Badge.name == badge.name).first():
                db.add(badge)
        
        db.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

# Run initialization if this script is executed directly
if __name__ == "__main__":
    init_db()
