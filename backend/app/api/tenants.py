"""
Tenants API Routes
Endpoints for tenant management with automatic invoice generation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date, timedelta
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.property import Property
from app.models.unit import Unit
from app.models.tenant import Tenant
from app.models.invoice import Invoice
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse, TenantMoveOut
from app.api.deps import get_current_user

router = APIRouter()


def generate_invoice_number(db: Session, year: int, month: int) -> str:
    """Generate unique invoice number"""
    import random
    while True:
        number = f"INV-{year}-{month:02d}-{random.randint(100000, 999999)}"
        existing = db.query(Invoice).filter(Invoice.invoice_number == number).first()
        if not existing:
            return number


@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(
    tenant_data: TenantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new tenant.
    
    **Automatic actions:**
    1. Creates tenant record
    2. Creates security deposit invoice (due in 5 days)
    3. Creates first month rent invoice (due on move-in date or 1st of month)
    4. Marks unit as unavailable
    5. Sets tenant status to 'pending' (becomes 'active' when both invoices paid)
    
    **Requires authentication.**
    """
    # Verify property ownership
    property = db.query(Property).filter(
        Property.id == tenant_data.property_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Verify unit exists and belongs to property
    unit = db.query(Unit).filter(
        Unit.id == tenant_data.unit_id,
        Unit.property_id == tenant_data.property_id
    ).first()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Check if unit is available
    if not unit.is_available:
        raise HTTPException(
            status_code=400,
            detail="Unit is not available"
        )
    
    # Create tenant
    db_tenant = Tenant(
        **tenant_data.dict(),
        status="pending",
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    db.add(db_tenant)
    db.flush()  # Get tenant ID
    
    # Mark unit as unavailable
    unit.is_available = False
    
    # Create invoices
    today = date.today()
    
    # 1. Security Deposit Invoice (due in 5 days)
    deposit_invoice = Invoice(
        tenant_id=db_tenant.id,
        property_id=tenant_data.property_id,
        unit_id=tenant_data.unit_id,
        invoice_number=generate_invoice_number(db, today.year, today.month),
        invoice_type="security_deposit",
        amount=tenant_data.security_deposit_amount,
        paid_amount=Decimal(0),
        credit_applied=Decimal(0),
        due_date=today + timedelta(days=5),
        status="unpaid",
        created_by=current_user.id
    )
    
    db.add(deposit_invoice)
    
    # 2. First Month Rent Invoice
    # Due date is move-in date or 1st of next month
    if tenant_data.move_in_date:
        first_rent_due = tenant_data.move_in_date
        rent_month = tenant_data.move_in_date.month
        rent_year = tenant_data.move_in_date.year
    else:
        # Default to 1st of next month
        if today.month == 12:
            rent_month = 1
            rent_year = today.year + 1
        else:
            rent_month = today.month + 1
            rent_year = today.year
        first_rent_due = date(rent_year, rent_month, 1)
    
    rent_invoice = Invoice(
        tenant_id=db_tenant.id,
        property_id=tenant_data.property_id,
        unit_id=tenant_data.unit_id,
        invoice_number=generate_invoice_number(db, rent_year, rent_month),
        invoice_type="monthly_rent",
        amount=tenant_data.base_rent,
        paid_amount=Decimal(0),
        credit_applied=Decimal(0),
        due_date=first_rent_due,
        month=rent_month,
        year=rent_year,
        status="unpaid",
        created_by=current_user.id
    )
    
    db.add(rent_invoice)
    
    db.commit()
    db.refresh(db_tenant)
    
    return db_tenant


@router.get("/tenants", response_model=list[TenantResponse])
def list_tenants(
    property_id: UUID = None,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all tenants.
    
    Filter by property_id or status (pending, active, moved_out).
    """
    query = db.query(Tenant).join(Property).filter(
        Property.landlord_id == current_user.id
    )
    
    if property_id:
        query = query.filter(Tenant.property_id == property_id)
    
    if status:
        query = query.filter(Tenant.status == status)
    
    tenants = query.order_by(Tenant.created_at.desc()).all()
    
    return tenants


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific tenant"""
    tenant = db.query(Tenant).join(Property).filter(
        Tenant.id == tenant_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return tenant


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update tenant information"""
    tenant = db.query(Tenant).join(Property).filter(
        Tenant.id == tenant_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Update fields
    update_data = tenant_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    
    tenant.updated_by = current_user.id
    
    db.commit()
    db.refresh(tenant)
    
    return tenant


@router.post("/tenants/{tenant_id}/move-out")
def process_move_out(
    tenant_id: UUID,
    move_out_data: TenantMoveOut,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process tenant move-out.
    
    Calculates security deposit refund:
    Refund = Security Deposit - (Unpaid Rent + Damages)
    """
    tenant = db.query(Tenant).join(Property).filter(
        Tenant.id == tenant_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant.status == "moved_out":
        raise HTTPException(status_code=400, detail="Tenant already moved out")
    
    # Update tenant
    tenant.move_out_date = move_out_data.move_out_date
    tenant.move_out_damages = move_out_data.damages
    tenant.move_out_unpaid_rent = move_out_data.unpaid_rent
    tenant.status = "moved_out"
    
    # Calculate refund
    refund = tenant.security_deposit_amount - (move_out_data.damages + move_out_data.unpaid_rent)
    if refund < 0:
        refund = Decimal(0)
    
    tenant.security_deposit_refund = refund
    tenant.updated_by = current_user.id
    
    # Mark unit as available
    unit = db.query(Unit).filter(Unit.id == tenant.unit_id).first()
    if unit:
        unit.is_available = True
    
    db.commit()
    
    return {
        "message": "Move-out processed successfully",
        "tenant_id": tenant.id,
        "security_deposit": float(tenant.security_deposit_amount),
        "damages": float(move_out_data.damages),
        "unpaid_rent": float(move_out_data.unpaid_rent),
        "refund_amount": float(refund)
    }


@router.post("/tenants/{tenant_id}/activate")
def activate_tenant_manually(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually activate a tenant or check activation status.
    
    Checks if both deposit and first rent are paid, then activates tenant.
    
    Useful if tenant was stuck in 'pending' due to payment order.
    """
    from app.models.invoice import Invoice
    
    tenant = db.query(Tenant).join(Property).filter(
        Tenant.id == tenant_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Check if deposit is paid
    deposit_invoice = db.query(Invoice).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_type == "security_deposit"
    ).first()
    
    deposit_paid = deposit_invoice and deposit_invoice.status == "paid"
    
    # Check if any rent is paid
    rent_invoice = db.query(Invoice).filter(
        Invoice.tenant_id == tenant_id,
        Invoice.invoice_type == "monthly_rent",
        Invoice.status == "paid"
    ).first()
    
    rent_paid = rent_invoice is not None
    
    # Activate if both paid
    if deposit_paid and rent_paid and tenant.status == "pending":
        tenant.status = "active"
        db.commit()
        db.refresh(tenant)
        
        return {
            "success": True,
            "message": "Tenant activated successfully!",
            "tenant_id": str(tenant.id),
            "status": "active",
            "deposit_paid": deposit_paid,
            "rent_paid": rent_paid
        }
    
    return {
        "success": False,
        "message": f"Tenant status: {tenant.status}",
        "tenant_id": str(tenant.id),
        "status": tenant.status,
        "deposit_paid": deposit_paid,
        "rent_paid": rent_paid,
        "can_activate": deposit_paid and rent_paid
    }


@router.get("/tenants/{tenant_id}/invoices", response_model=list)
def get_tenant_invoices(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all invoices for a tenant"""
    tenant = db.query(Tenant).join(Property).filter(
        Tenant.id == tenant_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    invoices = db.query(Invoice).filter(
        Invoice.tenant_id == tenant_id
    ).order_by(Invoice.due_date.desc()).all()
    
    return invoices


@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a tenant permanently.
    
    This will:
    - Delete the tenant record
    - Delete all associated invoices (cascade)
    - Delete all payment records (cascade)
    - Make the unit available again
    
    Note: Only moved-out tenants should be deleted.
    Active tenants should be moved out first.
    """
    # Find tenant and verify ownership
    tenant = db.query(Tenant).join(Property).filter(
        Tenant.id == tenant_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Optional: Prevent deleting active tenants
    if tenant.status == 'active':
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete active tenant. Please move them out first."
        )
    
    # Get the unit to mark as available
    unit = db.query(Unit).filter(Unit.id == tenant.unit_id).first()
    
    # Delete tenant (cascades to invoices and payments via database constraints)
    db.delete(tenant)
    
    # Mark unit as available if it was the tenant's unit
    if unit:
        unit.is_available = True
    
    db.commit()
    
    return None