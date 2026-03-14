"""
Unit Model
SQLAlchemy model for units (apartments/rooms) table
"""

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Unit(Base):
    """
    Unit model representing individual apartments/rooms in a property.
    
    Attributes:
        id: Unique unit identifier
        property_id: Property this unit belongs to
        unit_number: Unit identifier (A1, B2, etc.)
        bedrooms: Number of bedrooms
        bathrooms: Number of bathrooms
        size_sqm: Size in square meters
        base_rent: Monthly rent amount
        is_available: Whether unit is available for rent
        created_at: When unit was created
        updated_at: When unit was last updated
    """
    
    __tablename__ = "units"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_number = Column(String(50), nullable=False)
    bedrooms = Column(Integer, nullable=False, default=0)
    bathrooms = Column(Integer, nullable=False, default=1)
    size_sqm = Column(Numeric(10, 2), nullable=True)
    base_rent = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    def __repr__(self):
        return f"<Unit {self.unit_number}>"