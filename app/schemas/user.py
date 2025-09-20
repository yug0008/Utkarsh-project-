
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.user import UserRole, Gender

class UserBase(BaseModel):
    email: EmailStr
    name: str
    gender: Optional[Gender] = None
    location: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
