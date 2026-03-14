"""
Payment Model
SQLAlchemy model for payments table
"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Payment(Base):
    """
    Payment model for tracking all payments (M-Pesa, cash, bank transfer).
    
    Attributes:
        id: Unique payment identifier
        invoice_id: Invoice this payment is for (nullable for unmatched)
        tenant_id: Tenant who made payment (after matching)
        property_id: Property (for querying)
        trans_id: M-Pesa transaction ID (unique)
        amount: Payment amount
        msisdn: Payer phone number
        paybill_shortcode: M-Pesa paybill used
        bill_ref_number: Reference (unit number)
        first_name, middle_name, last_name: Payer names
        trans_time: Transaction timestamp
        payment_method: mpesa, cash, bank_transfer
        status: matched, unmatched, duplicate, failed
        matched_at: When payment was matched to invoice
    """
    
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True, index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # M-Pesa fields
    trans_id = Column(String(100), unique=True, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    msisdn = Column(String(20), nullable=True)
    paybill_shortcode = Column(String(20), nullable=True, index=True)
    bill_ref_number = Column(String(100), nullable=True, index=True)
    
    # Payer info
    first_name = Column(String(100), nullable=True)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Transaction details
    trans_time = Column(DateTime(timezone=True), nullable=True)
    payment_method = Column(String(50), nullable=False, default="mpesa")
    
    # Matching status
    status = Column(String(20), nullable=False, default="unmatched", index=True)
    matched_at = Column(DateTime(timezone=True), nullable=True)
    
    # Raw M-Pesa payload for debugging
    raw_payload = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Payment {self.trans_id}>"