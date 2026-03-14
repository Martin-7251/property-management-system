"""
Property API Routes
CRUD endpoints for property management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse, PropertyListResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/properties", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    property_data: PropertyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new property.
    
    **Requires authentication.**
    
    Each landlord can have multiple properties (buildings).
    
    **Example:**
    - Sunset Apartments
    - Garden View Flats
    - Downtown Studios
    """
    # Create new property
    db_property = Property(
        landlord_id=current_user.id,
        name=property_data.name,
        address=property_data.address,
        description=property_data.description,
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    
    return db_property


@router.get("/properties", response_model=PropertyListResponse)
def list_properties(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all properties for the current landlord.
    
    **Requires authentication.**
    
    **Pagination:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100)
    """
    # Get total count
    total = db.query(Property).filter(Property.landlord_id == current_user.id).count()
    
    # Get properties
    properties = db.query(Property)\
        .filter(Property.landlord_id == current_user.id)\
        .order_by(Property.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "total": total,
        "properties": properties
    }


@router.get("/properties/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific property by ID.
    
    **Requires authentication.**
    
    You can only view your own properties.
    """
    # Get property
    property = db.query(Property).filter(
        Property.id == property_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found or you don't have permission to view it"
        )
    
    return property


@router.put("/properties/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: UUID,
    property_data: PropertyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a property.
    
    **Requires authentication.**
    
    You can only update your own properties.
    Only provided fields will be updated.
    """
    # Get property
    property = db.query(Property).filter(
        Property.id == property_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found or you don't have permission to update it"
        )
    
    # Update fields
    update_data = property_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(property, field, value)
    
    property.updated_by = current_user.id
    
    db.commit()
    db.refresh(property)
    
    return property


@router.delete("/properties/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a property.
    
    **Requires authentication.**
    
    You can only delete your own properties.
    
    **Warning:** This will also delete all units, tenants, and invoices
    associated with this property (CASCADE delete).
    """
    # Get property
    property = db.query(Property).filter(
        Property.id == property_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found or you don't have permission to delete it"
        )
    
    db.delete(property)
    db.commit()
    
    return None


@router.get("/properties/{property_id}/summary")
def get_property_summary(
    property_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get property summary with statistics.
    
    **Requires authentication.**
    
    Returns:
    - Property details
    - Total units
    - Occupied units
    - Vacant units
    - Total tenants
    - (More stats will be added as we build other features)
    """
    # Get property
    property = db.query(Property).filter(
        Property.id == property_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found or you don't have permission to view it"
        )
    
    # For now, return basic info
    # We'll add more stats when we create Units and Tenants models
    return {
        "property": {
            "id": property.id,
            "name": property.name,
            "address": property.address,
            "description": property.description
        },
        "statistics": {
            "total_units": 0,  # Will update when we add Units
            "occupied_units": 0,
            "vacant_units": 0,
            "total_tenants": 0
        }
    }