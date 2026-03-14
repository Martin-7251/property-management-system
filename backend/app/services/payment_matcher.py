"""
Payment Matching Service
Automatically matches payments to invoices
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
import logging

from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.tenant import Tenant
from app.models.unit import Unit

logger = logging.getLogger(__name__)


class PaymentMatcher:
    """Service to match payments with invoices"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def match_payment(self, payment: Payment) -> bool:
        """
        Match a payment to an invoice.
        
        Matching logic:
        1. Find tenant by bill_ref_number (unit number or unit-DEP for deposit)
        2. Find unpaid invoices for that tenant
        3. Apply payment to oldest unpaid invoice first
        4. Update invoice status
        5. Mark payment as matched
        
        Args:
            payment: Payment object to match
            
        Returns:
            True if matched successfully, False otherwise
        """
        try:
            # Extract unit number from bill_ref_number
            bill_ref = payment.bill_ref_number
            if not bill_ref:
                logger.warning(f"Payment {payment.trans_id} has no bill reference")
                return False
            
            # Check if this is a deposit payment (format: UNIT-DEP)
            is_deposit = bill_ref.upper().endswith("-DEP")
            unit_number = bill_ref.replace("-DEP", "").replace("-dep", "")
            
            # Find unit by number and property's paybill
            unit = self.db.query(Unit).filter(
                Unit.unit_number == unit_number,
                Unit.property_id == payment.property_id
            ).first()
            
            if not unit:
                logger.warning(f"No unit found for bill ref: {bill_ref}")
                return False
            
            # Find active tenant for this unit
            tenant = self.db.query(Tenant).filter(
                Tenant.unit_id == unit.id,
                Tenant.status.in_(["pending", "active"])
            ).first()
            
            if not tenant:
                logger.warning(f"No tenant found for unit: {unit_number}")
                return False
            
            # Find appropriate invoice
            if is_deposit:
                # Find security deposit invoice
                invoice = self.db.query(Invoice).filter(
                    Invoice.tenant_id == tenant.id,
                    Invoice.invoice_type == "security_deposit",
                    Invoice.status.in_(["unpaid", "partially_paid"])
                ).first()
            else:
                # Find oldest unpaid rent invoice
                invoice = self.db.query(Invoice).filter(
                    Invoice.tenant_id == tenant.id,
                    Invoice.invoice_type == "monthly_rent",
                    Invoice.status.in_(["unpaid", "partially_paid"])
                ).order_by(Invoice.due_date.asc()).first()
            
            if not invoice:
                logger.warning(f"No unpaid invoice found for tenant: {tenant.full_name}")
                return False
            
            # Apply payment to invoice
            invoice.paid_amount += Decimal(str(payment.amount))
            
            # Update invoice status
            total_paid = invoice.paid_amount + invoice.credit_applied
            if total_paid >= invoice.amount:
                invoice.status = "paid"
                
                # If security deposit is paid, update tenant
                if invoice.invoice_type == "security_deposit":
                    tenant.security_deposit_paid = True
                    tenant.security_deposit_paid_date = payment.trans_time.date() if payment.trans_time else datetime.now().date()
                
                # Check if tenant should be activated (after ANY invoice is paid)
                # Tenant activates when BOTH deposit and first rent are paid
                if tenant.status == "pending":
                    # Check if deposit is paid
                    deposit_paid = self.db.query(Invoice).filter(
                        Invoice.tenant_id == tenant.id,
                        Invoice.invoice_type == "security_deposit",
                        Invoice.status == "paid"
                    ).first()
                    
                    # Check if any rent is paid
                    rent_paid = self.db.query(Invoice).filter(
                        Invoice.tenant_id == tenant.id,
                        Invoice.invoice_type == "monthly_rent",
                        Invoice.status == "paid"
                    ).first()
                    
                    # Activate if both are paid
                    if deposit_paid and rent_paid:
                        tenant.status = "active"
                        logger.info(f"Tenant {tenant.full_name} activated!")
                        
            elif total_paid > 0:
                invoice.status = "partially_paid"
            
            # Update payment
            payment.invoice_id = invoice.id
            payment.tenant_id = tenant.id
            payment.status = "matched"
            payment.matched_at = datetime.now()
            
            self.db.commit()
            
            logger.info(f"Payment {payment.trans_id} matched to invoice {invoice.invoice_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error matching payment {payment.trans_id}: {e}")
            self.db.rollback()
            return False
    
    def match_all_unmatched(self) -> int:
        """
        Attempt to match all unmatched payments.
        
        Returns:
            Number of payments successfully matched
        """
        unmatched = self.db.query(Payment).filter(
            Payment.status == "unmatched"
        ).all()
        
        matched_count = 0
        for payment in unmatched:
            if self.match_payment(payment):
                matched_count += 1
        
        return matched_count