"""
Payments API Routes
Endpoints for viewing and managing payments
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.property import Property
from app.models.payment import Payment
from app.api.deps import get_current_user
from app.services.payment_matcher import PaymentMatcher
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class PaymentResponse(BaseModel):
    """Schema for payment response"""
    id: UUID
    trans_id: str
    amount: Decimal
    msisdn: str | None
    paybill_shortcode: str | None
    bill_ref_number: str | None
    first_name: str | None
    last_name: str | None
    trans_time: datetime | None
    payment_method: str
    status: str
    matched_at: datetime | None
    invoice_id: UUID | None
    tenant_id: UUID | None
    created_at: datetime
    
    class Config:
        orm_mode = True


router = APIRouter()


@router.get("/payments", response_model=List[PaymentResponse])
def list_payments(
    property_id: UUID = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all payments.
    
    Filter by:
    - property_id: Specific property
    - status: matched, unmatched, duplicate, failed
    """
    query = db.query(Payment)
    
    # Filter by properties owned by current user
    if property_id:
        # Verify ownership
        property = db.query(Property).filter(
            Property.id == property_id,
            Property.landlord_id == current_user.id
        ).first()
        
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        query = query.filter(Payment.property_id == property_id)
    else:
        # Show all payments for user's properties
        user_property_ids = [p.id for p in db.query(Property).filter(
            Property.landlord_id == current_user.id
        ).all()]
        query = query.filter(Payment.property_id.in_(user_property_ids))
    
    if status:
        query = query.filter(Payment.status == status)
    
    payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    return payments


@router.get("/payments/unmatched", response_model=List[PaymentResponse])
def list_unmatched_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all unmatched payments.
    
    These need manual matching or investigation.
    """
    user_property_ids = [p.id for p in db.query(Property).filter(
        Property.landlord_id == current_user.id
    ).all()]
    
    payments = db.query(Payment).filter(
        Payment.property_id.in_(user_property_ids),
        Payment.status == "unmatched"
    ).order_by(Payment.created_at.desc()).all()
    
    return payments


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific payment"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify ownership
    if payment.property_id:
        property = db.query(Property).filter(
            Property.id == payment.property_id,
            Property.landlord_id == current_user.id
        ).first()
        
        if not property:
            raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment


@router.post("/payments/{payment_id}/match")
def manually_match_payment(
    payment_id: UUID,
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually match a payment to an invoice.
    
    Use this for unmatched payments that couldn't be auto-matched.
    """
    from app.models.invoice import Invoice
    from decimal import Decimal
    
    # Get payment
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify property ownership
    if payment.property_id:
        property = db.query(Property).filter(
            Property.id == payment.property_id,
            Property.landlord_id == current_user.id
        ).first()
        if not property:
            raise HTTPException(status_code=404, detail="Payment not found")
    
    # Get invoice
    invoice = db.query(Invoice).join(Property).filter(
        Invoice.id == invoice_id,
        Property.landlord_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Match payment
    payment.invoice_id = invoice.id
    payment.tenant_id = invoice.tenant_id
    payment.status = "matched"
    payment.matched_at = datetime.now()
    
    # Update invoice
    invoice.paid_amount += Decimal(str(payment.amount))
    
    total_paid = invoice.paid_amount + invoice.credit_applied
    if total_paid >= invoice.amount:
        invoice.status = "paid"
    elif total_paid > 0:
        invoice.status = "partially_paid"
    
    db.commit()
    
    return {
        "success": True,
        "message": "Payment matched successfully",
        "payment_id": str(payment.id),
        "invoice_id": str(invoice.id)
    }


@router.post("/payments/match-all")
def match_all_unmatched(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Attempt to auto-match all unmatched payments.
    
    Useful after adding new tenants or invoices.
    """
    matcher = PaymentMatcher(db)
    matched_count = matcher.match_all_unmatched()
    
    return {
        "success": True,
        "matched_count": matched_count,
        "message": f"Successfully matched {matched_count} payment(s)"
    }