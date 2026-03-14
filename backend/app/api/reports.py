"""
Reports API Routes
Financial and operational reports
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.property import Property
from app.models.unit import Unit
from app.models.tenant import Tenant
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/reports/revenue")
def revenue_report(
    property_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revenue report showing payments received.
    
    **Filter by:**
    - property_id: Specific property
    - start_date: From date
    - end_date: To date
    """
    # Get user's properties
    properties_query = db.query(Property).filter(Property.landlord_id == current_user.id)
    
    if property_id:
        properties_query = properties_query.filter(Property.id == property_id)
    
    user_property_ids = [p.id for p in properties_query.all()]
    
    # Build payment query
    query = db.query(Payment).filter(
        Payment.property_id.in_(user_property_ids),
        Payment.status == "matched"
    )
    
    if start_date:
        query = query.filter(Payment.trans_time >= start_date)
    if end_date:
        query = query.filter(Payment.trans_time <= end_date)
    
    # Get totals
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.property_id.in_(user_property_ids),
        Payment.status == "matched"
    )
    
    if start_date:
        total_revenue = total_revenue.filter(Payment.trans_time >= start_date)
    if end_date:
        total_revenue = total_revenue.filter(Payment.trans_time <= end_date)
    
    total_revenue = total_revenue.scalar() or 0
    
    # Get payment count
    payment_count = query.count()
    
    # Get revenue by property
    revenue_by_property = db.query(
        Property.name,
        Property.id,
        func.sum(Payment.amount).label('total')
    ).join(Payment, Payment.property_id == Property.id).filter(
        Property.landlord_id == current_user.id,
        Payment.status == "matched"
    )
    
    if start_date:
        revenue_by_property = revenue_by_property.filter(Payment.trans_time >= start_date)
    if end_date:
        revenue_by_property = revenue_by_property.filter(Payment.trans_time <= end_date)
    
    revenue_by_property = revenue_by_property.group_by(Property.id).all()
    
    # Recent payments
    recent_payments = query.order_by(Payment.trans_time.desc()).limit(10).all()
    
    return {
        "summary": {
            "total_revenue": float(total_revenue),
            "payment_count": payment_count,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        },
        "by_property": [
            {
                "property_name": row[0],
                "property_id": str(row[1]),
                "revenue": float(row[2])
            }
            for row in revenue_by_property
        ],
        "recent_payments": [
            {
                "trans_id": p.trans_id,
                "amount": float(p.amount),
                "date": p.trans_time.isoformat() if p.trans_time else None,
                "tenant_id": str(p.tenant_id) if p.tenant_id else None
            }
            for p in recent_payments
        ]
    }


@router.get("/reports/occupancy")
def occupancy_report(
    property_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Occupancy report showing units occupied vs vacant.
    
    **Filter by:**
    - property_id: Specific property
    """
    # Get user's properties
    properties_query = db.query(Property).filter(Property.landlord_id == current_user.id)
    
    if property_id:
        properties_query = properties_query.filter(Property.id == property_id)
    
    properties = properties_query.all()
    
    report_data = []
    
    for prop in properties:
        # Count units
        total_units = db.query(Unit).filter(Unit.property_id == prop.id).count()
        occupied_units = db.query(Unit).filter(
            Unit.property_id == prop.id,
            Unit.is_available == False
        ).count()
        vacant_units = total_units - occupied_units
        
        # Count tenants
        total_tenants = db.query(Tenant).filter(
            Tenant.property_id == prop.id,
            Tenant.status.in_(["pending", "active"])
        ).count()
        
        # Calculate occupancy rate
        occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
        
        # Calculate potential revenue
        total_rent = db.query(func.sum(Unit.base_rent)).filter(
            Unit.property_id == prop.id
        ).scalar() or 0
        
        actual_rent = db.query(func.sum(Tenant.base_rent)).filter(
            Tenant.property_id == prop.id,
            Tenant.status == "active"
        ).scalar() or 0
        
        report_data.append({
            "property_id": str(prop.id),
            "property_name": prop.name,
            "total_units": total_units,
            "occupied_units": occupied_units,
            "vacant_units": vacant_units,
            "occupancy_rate": round(occupancy_rate, 2),
            "total_tenants": total_tenants,
            "potential_monthly_rent": float(total_rent),
            "actual_monthly_rent": float(actual_rent),
            "vacancy_loss": float(total_rent - actual_rent)
        })
    
    # Overall summary
    overall = {
        "total_units": sum(r["total_units"] for r in report_data),
        "occupied_units": sum(r["occupied_units"] for r in report_data),
        "vacant_units": sum(r["vacant_units"] for r in report_data),
        "total_tenants": sum(r["total_tenants"] for r in report_data),
        "potential_monthly_rent": sum(r["potential_monthly_rent"] for r in report_data),
        "actual_monthly_rent": sum(r["actual_monthly_rent"] for r in report_data)
    }
    
    overall["occupancy_rate"] = (
        overall["occupied_units"] / overall["total_units"] * 100
        if overall["total_units"] > 0 else 0
    )
    
    return {
        "summary": overall,
        "by_property": report_data
    }


@router.get("/reports/arrears")
def arrears_report(
    property_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Arrears report showing unpaid/overdue invoices.
    
    **Filter by:**
    - property_id: Specific property
    """
    # Get user's properties
    properties_query = db.query(Property).filter(Property.landlord_id == current_user.id)
    
    if property_id:
        properties_query = properties_query.filter(Property.id == property_id)
    
    user_property_ids = [p.id for p in properties_query.all()]
    
    # Get unpaid invoices
    unpaid_invoices = db.query(Invoice).filter(
        Invoice.property_id.in_(user_property_ids),
        Invoice.status.in_(["unpaid", "partially_paid", "overdue"])
    ).all()
    
    # Calculate totals
    total_arrears = sum(
        float(inv.amount - inv.paid_amount - inv.credit_applied)
        for inv in unpaid_invoices
    )
    
    overdue_invoices = [inv for inv in unpaid_invoices if inv.status == "overdue"]
    total_overdue = sum(
        float(inv.amount - inv.paid_amount - inv.credit_applied)
        for inv in overdue_invoices
    )
    
    # Group by tenant
    tenants_in_arrears = {}
    
    for invoice in unpaid_invoices:
        tenant = db.query(Tenant).filter(Tenant.id == invoice.tenant_id).first()
        if not tenant:
            continue
        
        tenant_id = str(tenant.id)
        
        if tenant_id not in tenants_in_arrears:
            unit = db.query(Unit).filter(Unit.id == tenant.unit_id).first()
            tenants_in_arrears[tenant_id] = {
                "tenant_id": tenant_id,
                "tenant_name": tenant.full_name,
                "phone": tenant.phone,
                "unit_number": unit.unit_number if unit else "N/A",
                "total_arrears": 0,
                "invoices": []
            }
        
        balance = float(invoice.amount - invoice.paid_amount - invoice.credit_applied)
        tenants_in_arrears[tenant_id]["total_arrears"] += balance
        tenants_in_arrears[tenant_id]["invoices"].append({
            "invoice_number": invoice.invoice_number,
            "invoice_type": invoice.invoice_type,
            "amount": float(invoice.amount),
            "paid": float(invoice.paid_amount),
            "balance": balance,
            "due_date": invoice.due_date.isoformat(),
            "status": invoice.status
        })
    
    # Sort by total arrears (highest first)
    tenants_list = sorted(
        tenants_in_arrears.values(),
        key=lambda x: x["total_arrears"],
        reverse=True
    )
    
    return {
        "summary": {
            "total_arrears": total_arrears,
            "total_overdue": total_overdue,
            "total_unpaid_invoices": len(unpaid_invoices),
            "total_overdue_invoices": len(overdue_invoices),
            "tenants_in_arrears": len(tenants_list)
        },
        "tenants": tenants_list
    }


@router.get("/reports/dashboard")
def dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard summary with key metrics.
    
    Returns overview of entire portfolio.
    """
    # Get all properties
    user_property_ids = [
        p.id for p in db.query(Property).filter(
            Property.landlord_id == current_user.id
        ).all()
    ]
    
    # Properties count
    total_properties = len(user_property_ids)
    
    # Units
    total_units = db.query(Unit).filter(
        Unit.property_id.in_(user_property_ids)
    ).count()
    
    occupied_units = db.query(Unit).filter(
        Unit.property_id.in_(user_property_ids),
        Unit.is_available == False
    ).count()
    
    # Tenants
    active_tenants = db.query(Tenant).filter(
        Tenant.property_id.in_(user_property_ids),
        Tenant.status == "active"
    ).count()
    
    # Revenue (this month)
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    month_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.property_id.in_(user_property_ids),
        Payment.status == "matched",
        Payment.trans_time >= month_start
    ).scalar() or 0
    
    # Arrears
    total_arrears = db.query(
        func.sum(Invoice.amount - Invoice.paid_amount - Invoice.credit_applied)
    ).filter(
        Invoice.property_id.in_(user_property_ids),
        Invoice.status.in_(["unpaid", "partially_paid", "overdue"])
    ).scalar() or 0
    
    # Occupancy rate
    occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
    
    return {
        "properties": total_properties,
        "units": {
            "total": total_units,
            "occupied": occupied_units,
            "vacant": total_units - occupied_units,
            "occupancy_rate": round(occupancy_rate, 2)
        },
        "tenants": {
            "active": active_tenants
        },
        "revenue": {
            "this_month": float(month_revenue)
        },
        "arrears": {
            "total": float(total_arrears)
        }
    }