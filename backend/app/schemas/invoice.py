"""
Invoice Schemas
Pydantic models for invoice API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class InvoiceBase(BaseModel):
    """Base invoice schema"""
    amount: Decimal = Field(..., gt=0)
    due_date: date


class InvoiceResponse(BaseModel):
    """Schema for invoice response"""
    id: UUID
    tenant_id: UUID
    property_id: UUID
    unit_id: UUID
    invoice_number: Optional[str]
    invoice_type: str
    amount: Decimal
    paid_amount: Decimal
    credit_applied: Decimal
    due_date: date
    month: Optional[int]
    year: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class InvoiceUpdate(BaseModel):
    """Schema for updating invoice"""
    amount: Optional[Decimal] = Field(None, gt=0)
    due_date: Optional[date] = None