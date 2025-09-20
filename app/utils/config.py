
import os
from pydantic import BaseSettings, AnyUrl, validator
from typing import List, Optional

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    python_version: str = "3.9.12"
    port: int = 8000
    
    # Database
    database_url: AnyUrl
    dev_database_url: AnyUrl = "sqlite:///./dev.db"
    test_database_url: AnyUrl = "sqlite:///./test.db"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    dev_frontend_url: str = "http://localhost:3000"
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "https://nextchampion.vercel.app",
        "https://nextchampion.netlify.app"
    ]
    
    # File Uploads
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "sports-talent-videos"
    upload_dir: str = "uploads"
    max_file_size_mb: int = 100
    
    # AI Processing
    mediapipe_model_complexity: int = 1
    mediapipe_min_detection_confidence: float = 0.5
    mediapipe_min_tracking_confidence: float = 0.5
    ai_processing_timeout: int = 300
    
    class Config:
        env_file = ".env"
        
    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
        
    def get_database_url(self):
        if self.environment == "testing":
            return self.test_database_url
        elif self.environment == "development":
            return self.dev_database_url
        else:
            return self.database_url

settings = Settings()
