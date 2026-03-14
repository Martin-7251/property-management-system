"""
Invoices API Routes
Endpoints for invoice management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.property import Property
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceResponse, InvoiceUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/invoices", response_model=list[InvoiceResponse])
def list_invoices(
    property_id: UUID = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all invoices.
    
    Filter by property_id or status (unpaid, partially_paid, paid, overdue).
    """
    query = db.query(Invoice).join(Property).filter(
        Property.landlord_id == current_user.id
    )
    
    if property_id:
        query = query.filter(Invoice.property_id == property_id)
    
    if status:
        query = query.filter(Invoice.status == status)
    
    invoices = query.order_by(Invoice.due_date.desc()).offset(skip).limit(limit).all()
    
    return invoices


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific invoice"""
    invoice = db.query(Invoice).join(Property).filter(
        Invoice.id == invoice_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return invoice


@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: UUID,
    invoice_data: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update invoice (adjust amount or due date).
    
    Useful for giving discounts or extending payment deadlines.
    """
    invoice = db.query(Invoice).join(Property).filter(
        Invoice.id == invoice_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Update fields
    update_data = invoice_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    # Recalculate status
    total_paid = invoice.paid_amount + invoice.credit_applied
    if total_paid >= invoice.amount:
        invoice.status = "paid"
    elif total_paid > 0:
        invoice.status = "partially_paid"
    else:
        invoice.status = "unpaid"
    
    db.commit()
    db.refresh(invoice)
    
    return invoice


@router.get("/invoices/unpaid/summary")
def get_unpaid_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of unpaid invoices.
    
    Returns total amount unpaid and count.
    """
    from sqlalchemy import func
    
    result = db.query(
        func.count(Invoice.id).label("count"),
        func.sum(Invoice.amount - Invoice.paid_amount - Invoice.credit_applied).label("total")
    ).join(Property).filter(
        Property.landlord_id == current_user.id,
        Invoice.status.in_(["unpaid", "partially_paid", "overdue"])
    ).first()
    
    return {
        "unpaid_count": result.count or 0,
        "unpaid_total": float(result.total or 0)
    }