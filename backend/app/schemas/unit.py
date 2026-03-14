"""
Unit Schemas
Pydantic models for unit API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class UnitBase(BaseModel):
    """Base unit schema"""
    unit_number: str = Field(..., min_length=1, max_length=50)
    bedrooms: int = Field(..., ge=0, le=10)
    bathrooms: int = Field(..., ge=0, le=10)
    size_sqm: Optional[Decimal] = Field(None, ge=0)
    base_rent: Decimal = Field(..., gt=0)


class UnitCreate(UnitBase):
    """Schema for creating a unit"""
    property_id: UUID
    
    class Config:
        schema_extra = {
            "example": {
                "property_id": "550e8400-e29b-41d4-a716-446655440000",
                "unit_number": "A1",
                "bedrooms": 2,
                "bathrooms": 1,
                "size_sqm": 75.5,
                "base_rent": 25000.00
            }
        }


class UnitUpdate(BaseModel):
    """Schema for updating a unit"""
    unit_number: Optional[str] = Field(None, min_length=1, max_length=50)
    bedrooms: Optional[int] = Field(None, ge=0, le=10)
    bathrooms: Optional[int] = Field(None, ge=0, le=10)
    size_sqm: Optional[Decimal] = Field(None, ge=0)
    base_rent: Optional[Decimal] = Field(None, gt=0)
    is_available: Optional[bool] = None


class UnitResponse(UnitBase):
    """Schema for unit response"""
    id: UUID
    property_id: UUID
    is_available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True