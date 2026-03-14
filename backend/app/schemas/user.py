"""
User Schemas - Pydantic v1 Compatible
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., regex=r'^\+[1-9]\d{1,14}$')  # E.164 format


class UserCreate(UserBase):
    """Schema for creating a new user (registration)"""
    password: str = Field(..., min_length=8, max_length=100)
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "phone": "+254712345678",
                "password": "SecurePassword123!"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePassword123!"
            }
        }


class UserResponse(UserBase):
    """Schema for user response (without password)"""
    id: UUID
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True  # This is the Pydantic v1 way!


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, regex=r'^\+[1-9]\d{1,14}$')
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "John Updated Doe",
                "phone": "+254722222222"
            }
        }


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data"""
    user_id: Optional[str] = None