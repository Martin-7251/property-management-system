"""
Property Schemas
Pydantic models for property API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class PropertyBase(BaseModel):
    """Base property schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Property name")
    address: str = Field(..., min_length=1, description="Full property address")
    description: Optional[str] = Field(None, description="Additional property details")


class PropertyCreate(PropertyBase):
    """Schema for creating a new property"""
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Sunset Apartments",
                "address": "Kilimani Road, Nairobi, Kenya",
                "description": "Modern 12-unit apartment building with secure parking and 24/7 security"
            }
        }


class PropertyUpdate(BaseModel):
    """Schema for updating property information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Sunset Apartments - Updated",
                "address": "123 Kilimani Road, Nairobi, Kenya",
                "description": "Modern apartment with new renovations"
            }
        }


class PropertyResponse(PropertyBase):
    """Schema for property response"""
    id: UUID
    landlord_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    
    class Config:
        orm_mode = True


class PropertyListResponse(BaseModel):
    """Schema for list of properties"""
    total: int
    properties: list[PropertyResponse]