"""
User Model
SQLAlchemy model for users table
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    """
    User model representing landlords and admins.
    
    Attributes:
        id: Unique user identifier (UUID)
        email: User email (unique, used for login)
        password_hash: Hashed password
        full_name: User's full name
        phone: Phone number with country code
        role: User role (landlord, admin)
        is_active: Whether account is active
        created_at: When user was created
        updated_at: When user was last updated
    """
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    role = Column(String(50), nullable=False, default="landlord")
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.email}>"