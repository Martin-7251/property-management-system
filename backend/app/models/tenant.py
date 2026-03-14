"""
Tenant Model
SQLAlchemy model for tenants table
"""

from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Date, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class TenantStatus(str, enum.Enum):
    """Tenant status enum"""
    PENDING = "pending"
    ACTIVE = "active"
    MOVED_OUT = "moved_out"


class Tenant(Base):
    """
    Tenant model representing renters.
    
    Attributes:
        id: Unique tenant identifier
        unit_id: Unit being rented
        property_id: Property (for easy querying)
        full_name: Tenant's full name
        phone: Phone number
        email: Email address
        id_number: National ID or passport
        base_rent: Monthly rent amount
        security_deposit_amount: Security deposit amount
        security_deposit_paid: Whether deposit is paid
        move_in_date: Date tenant moved in
        move_out_date: Date tenant moved out
        status: pending, active, moved_out
    """
    
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("units.id", ondelete="RESTRICT"), nullable=False, index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Personal info
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    id_number = Column(String(50), nullable=True)
    
    # Financial
    base_rent = Column(Numeric(10, 2), nullable=False)
    security_deposit_amount = Column(Numeric(10, 2), nullable=False)
    security_deposit_paid = Column(Boolean, default=False)
    security_deposit_paid_date = Column(Date, nullable=True)
    
    # Dates
    move_in_date = Column(Date, nullable=True)
    move_out_date = Column(Date, nullable=True)
    
    # Move-out settlement
    move_out_damages = Column(Numeric(10, 2), default=0, nullable=True)
    move_out_unpaid_rent = Column(Numeric(10, 2), default=0, nullable=True)
    security_deposit_refund = Column(Numeric(10, 2), nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default="pending", index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    def __repr__(self):
        return f"<Tenant {self.full_name}>"