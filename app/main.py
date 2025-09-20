
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, athletes, coaches, admin, gamification, ai_processing

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sports Talent Ecosystem API",
    description="AI-Powered Sports Talent Discovery Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(athletes.router)
app.include_router(coaches.router)
app.include_router(admin.router)
app.include_router(gamification.router)
app.include_router(ai_processing.router)

@app.get("/")
def root():
    return {"message": "Welcome to Sports Talent Ecosystem API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
