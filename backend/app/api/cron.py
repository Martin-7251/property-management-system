"""
Cron Jobs API
Endpoints to manually trigger automated tasks (for testing)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.invoice_generator import InvoiceGenerator

router = APIRouter()


@router.post("/cron/generate-monthly-invoices")
def trigger_monthly_invoices(
    month: int = None,
    year: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger monthly invoice generation.
    
    In production, this runs automatically on the 1st of each month.
    
    **Requires authentication.**
    
    Args:
    - month: Target month (1-12), default: next month
    - year: Target year, default: current/next year
    """
    generator = InvoiceGenerator(db)
    result = generator.generate_monthly_invoices(month, year)
    
    return result


@router.post("/cron/mark-overdue")
def trigger_overdue_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger overdue invoice check.
    
    Marks invoices past due date as 'overdue'.
    
    In production, this runs daily.
    
    **Requires authentication.**
    """
    generator = InvoiceGenerator(db)
    count = generator.check_overdue_invoices()
    
    return {
        "success": True,
        "overdue_count": count,
        "message": f"Marked {count} invoice(s) as overdue"
    }