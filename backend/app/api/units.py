"""
Units API Routes
CRUD endpoints for unit management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.property import Property
from app.models.unit import Unit
from app.schemas.unit import UnitCreate, UnitUpdate, UnitResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/units", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    unit_data: UnitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new unit in a property.
    
    **Requires authentication.**
    
    Units are apartments/rooms within a property.
    """
    # Verify property belongs to current user
    property = db.query(Property).filter(
        Property.id == unit_data.property_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found or you don't have permission"
        )
    
    # Check if unit number already exists in this property
    existing = db.query(Unit).filter(
        Unit.property_id == unit_data.property_id,
        Unit.unit_number == unit_data.unit_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unit {unit_data.unit_number} already exists in this property"
        )
    
    # Create unit
    db_unit = Unit(
        **unit_data.dict(),
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    
    return db_unit


@router.get("/properties/{property_id}/units", response_model=list[UnitResponse])
def list_property_units(
    property_id: UUID,
    available_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all units in a property.
    
    **Requires authentication.**
    
    Query params:
    - available_only: Only show available units
    """
    # Verify property ownership
    property = db.query(Property).filter(
        Property.id == property_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    query = db.query(Unit).filter(Unit.property_id == property_id)
    
    if available_only:
        query = query.filter(Unit.is_available == True)
    
    units = query.order_by(Unit.unit_number).all()
    
    return units


@router.get("/units/{unit_id}", response_model=UnitResponse)
def get_unit(
    unit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific unit"""
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Verify ownership through property
    property = db.query(Property).filter(
        Property.id == unit.property_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return unit


@router.put("/units/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: UUID,
    unit_data: UnitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a unit"""
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Verify ownership
    property = db.query(Property).filter(
        Property.id == unit.property_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Update fields
    update_data = unit_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(unit, field, value)
    
    unit.updated_by = current_user.id
    
    db.commit()
    db.refresh(unit)
    
    return unit


@router.delete("/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    unit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a unit.
    
    Cannot delete if unit has tenants.
    """
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Verify ownership
    property = db.query(Property).filter(
        Property.id == unit.property_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    db.delete(unit)
    db.commit()
    
    return None