"""
Monthly Invoice Generator
Automated service to generate rent invoices on 1st of each month
"""

from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal
import logging
from typing import List

from app.models.tenant import Tenant
from app.models.invoice import Invoice

logger = logging.getLogger(__name__)


class InvoiceGenerator:
    """Service to generate monthly rent invoices"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_invoice_number(self, year: int, month: int) -> str:
        """Generate unique invoice number"""
        import random
        while True:
            number = f"INV-{year}-{month:02d}-{random.randint(100000, 999999)}"
            existing = self.db.query(Invoice).filter(Invoice.invoice_number == number).first()
            if not existing:
                return number
    
    def generate_monthly_invoices(self, target_month: int = None, target_year: int = None) -> dict:
        """
        Generate monthly rent invoices for all active tenants.
        
        Args:
            target_month: Month to generate for (default: next month)
            target_year: Year to generate for (default: current/next year)
            
        Returns:
            Dictionary with results
        """
        today = date.today()
        
        # Determine target month/year
        if target_month is None or target_year is None:
            if today.month == 12:
                target_month = 1
                target_year = today.year + 1
            else:
                target_month = today.month + 1
                target_year = today.year
        
        # Due date is 10th of target month
        due_date = date(target_year, target_month, 10)
        
        # Get all active tenants
        active_tenants = self.db.query(Tenant).filter(
            Tenant.status == "active"
        ).all()
        
        created_count = 0
        skipped_count = 0
        errors = []
        
        for tenant in active_tenants:
            try:
                # Check if invoice already exists for this month
                existing = self.db.query(Invoice).filter(
                    Invoice.tenant_id == tenant.id,
                    Invoice.invoice_type == "monthly_rent",
                    Invoice.month == target_month,
                    Invoice.year == target_year
                ).first()
                
                if existing:
                    logger.info(f"Invoice already exists for tenant {tenant.full_name} - {target_year}-{target_month}")
                    skipped_count += 1
                    continue
                
                # Create invoice
                invoice = Invoice(
                    tenant_id=tenant.id,
                    property_id=tenant.property_id,
                    unit_id=tenant.unit_id,
                    invoice_number=self.generate_invoice_number(target_year, target_month),
                    invoice_type="monthly_rent",
                    amount=tenant.base_rent,
                    paid_amount=Decimal(0),
                    credit_applied=Decimal(0),
                    due_date=due_date,
                    month=target_month,
                    year=target_year,
                    status="unpaid"
                )
                
                self.db.add(invoice)
                created_count += 1
                
                logger.info(f"Created invoice for {tenant.full_name} - {invoice.invoice_number}")
                
            except Exception as e:
                error_msg = f"Error creating invoice for tenant {tenant.id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Commit all at once
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to commit invoices: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        
        return {
            "success": True,
            "month": target_month,
            "year": target_year,
            "created": created_count,
            "skipped": skipped_count,
            "total_tenants": len(active_tenants),
            "errors": errors
        }
    
    def check_overdue_invoices(self) -> int:
        """
        Mark overdue invoices.
        
        Invoices past due date with status 'unpaid' or 'partially_paid'
        should be marked as 'overdue'.
        
        Returns:
            Number of invoices marked as overdue
        """
        today = date.today()
        
        overdue_invoices = self.db.query(Invoice).filter(
            Invoice.due_date < today,
            Invoice.status.in_(["unpaid", "partially_paid"])
        ).all()
        
        for invoice in overdue_invoices:
            invoice.status = "overdue"
        
        try:
            self.db.commit()
            logger.info(f"Marked {len(overdue_invoices)} invoices as overdue")
            return len(overdue_invoices)
        except Exception as e:
            logger.error(f"Error marking invoices as overdue: {e}")
            self.db.rollback()
            return 0