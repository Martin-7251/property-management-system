"""
Invoice Model
SQLAlchemy model for invoices table
"""

from sqlalchemy import Column, String, Integer, Numeric, DateTime, Date, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class InvoiceType(str, enum.Enum):
    """Invoice type enum"""
    MONTHLY_RENT = "monthly_rent"
    SECURITY_DEPOSIT = "security_deposit"


class InvoiceStatus(str, enum.Enum):
    """Invoice status enum"""
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"


class Invoice(Base):
    """
    Invoice model for rent and security deposit billing.
    
    Attributes:
        id: Unique invoice identifier
        tenant_id: Tenant being invoiced
        property_id: Property (for querying)
        unit_id: Unit (for reference)
        invoice_number: Auto-generated invoice number
        invoice_type: monthly_rent or security_deposit
        amount: Total amount due
        paid_amount: Amount paid so far
        credit_applied: Credits applied to this invoice
        due_date: Payment due date
        month: Month (for rent invoices)
        year: Year (for rent invoices)
        status: unpaid, partially_paid, paid, overdue
    """
    
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("units.id", ondelete="CASCADE"), nullable=False)
    
    invoice_number = Column(String(50), unique=True, nullable=True, index=True)
    invoice_type = Column(String(50), nullable=False, index=True)
    
    amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0, nullable=False)
    credit_applied = Column(Numeric(10, 2), default=0, nullable=False)
    
    due_date = Column(Date, nullable=False, index=True)
    month = Column(Integer, nullable=True, index=True)
    year = Column(Integer, nullable=True, index=True)
    
    status = Column(String(20), nullable=False, default="unpaid", index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"