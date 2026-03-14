"""
Tenant Schemas
Pydantic models for tenant API requests and responses
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class TenantBase(BaseModel):
    """Base tenant schema"""
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., regex=r'^\+[1-9]\d{1,14}$')
    email: Optional[EmailStr] = None
    id_number: Optional[str] = Field(None, max_length=50)


class TenantCreate(TenantBase):
    """Schema for creating a tenant"""
    unit_id: UUID
    property_id: UUID
    base_rent: Decimal = Field(..., gt=0)
    security_deposit_amount: Decimal = Field(..., gt=0)
    move_in_date: Optional[date] = None
    
    class Config:
        schema_extra = {
            "example": {
                "unit_id": "550e8400-e29b-41d4-a716-446655440000",
                "property_id": "660e8400-e29b-41d4-a716-446655440000",
                "full_name": "Alice Wanjiku",
                "phone": "+254722111111",
                "email": "alice@example.com",
                "id_number": "12345678",
                "base_rent": 25000.00,
                "security_deposit_amount": 25000.00,
                "move_in_date": "2026-03-01"
            }
        }


class TenantUpdate(BaseModel):
    """Schema for updating tenant"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, regex=r'^\+[1-9]\d{1,14}$')
    email: Optional[EmailStr] = None
    id_number: Optional[str] = None
    base_rent: Optional[Decimal] = Field(None, gt=0)


class TenantResponse(TenantBase):
    """Schema for tenant response"""
    id: UUID
    unit_id: UUID
    property_id: UUID
    base_rent: Decimal
    security_deposit_amount: Decimal
    security_deposit_paid: bool
    security_deposit_paid_date: Optional[date]
    move_in_date: Optional[date]
    move_out_date: Optional[date]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class TenantMoveOut(BaseModel):
    """Schema for tenant move-out"""
    move_out_date: date
    damages: Decimal = Field(default=0, ge=0)
    unpaid_rent: Decimal = Field(default=0, ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "move_out_date": "2026-12-31",
                "damages": 5000.00,
                "unpaid_rent": 0.00
            }
        }