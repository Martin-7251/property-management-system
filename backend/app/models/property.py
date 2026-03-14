"""
Property Model
SQLAlchemy model for properties table
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Property(Base):
    """
    Property model representing buildings/complexes owned by landlords.
    
    Attributes:
        id: Unique property identifier (UUID)
        landlord_id: Owner of the property (foreign key to users)
        name: Property name
        address: Full address
        description: Additional details about the property
        created_at: When property was created
        updated_at: When property was last updated
        created_by: User who created the property
        updated_by: User who last updated the property
    """
    
    __tablename__ = "properties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    landlord_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships (we'll add these as we create other models)
    # landlord = relationship("User", foreign_keys=[landlord_id], back_populates="properties")
    # units = relationship("Unit", back_populates="property", cascade="all, delete-orphan")
    # mpesa_config = relationship("MpesaConfig", back_populates="property", uselist=False)
    
    def __repr__(self):
        return f"<Property {self.name}>"