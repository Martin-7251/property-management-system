"""
M-Pesa Config Model
SQLAlchemy model for M-Pesa configuration per property
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class MpesaConfig(Base):
    """
    M-Pesa configuration for each property.
    
    Each property has its own M-Pesa paybill/till number.
    
    Attributes:
        id: Unique identifier
        property_id: Property this config belongs to
        paybill_shortcode: M-Pesa paybill/till number
        consumer_key: Daraja API consumer key (encrypted)
        consumer_secret: Daraja API consumer secret (encrypted)
        passkey: M-Pesa passkey (encrypted)
        environment: sandbox or production
        validation_url: Callback URL for validation
        confirmation_url: Callback URL for confirmation
    """
    
    __tablename__ = "mpesa_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # M-Pesa credentials (should be encrypted in production)
    paybill_shortcode = Column(String(20), nullable=False, index=True)
    consumer_key = Column(String(500), nullable=False)
    consumer_secret = Column(String(500), nullable=False)
    passkey = Column(String(500), nullable=True)
    
    # Environment
    environment = Column(String(20), nullable=False, default="sandbox")
    
    # Callback URLs
    validation_url = Column(String(500), nullable=True)
    confirmation_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<MpesaConfig {self.paybill_shortcode}>"