"""
Export API Routes
Generate PDF and Excel reports for download
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.property import Property
from app.models.unit import Unit
from app.models.tenant import Tenant
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.api.deps import get_current_user
from app.utils.export import PDFExporter, ExcelExporter, format_currency, format_date

router = APIRouter()


@router.get("/export/tenants/pdf")
async def export_tenants_pdf(
    property_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export tenants list as PDF"""
    
    # Query tenants
    query = db.query(Tenant).join(Property).filter(
        Property.landlord_id == current_user.id
    )
    
    if property_id:
        query = query.filter(Tenant.property_id == property_id)
    if status:
        query = query.filter(Tenant.status == status)
    
    tenants = query.order_by(Tenant.full_name).all()
    
    # Create PDF
    pdf = PDFExporter(title="Tenants Report")
    pdf.add_title("Tenants Report")
    pdf.add_paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    pdf.add_paragraph(f"Total Tenants: {len(tenants)}")
    pdf.add_spacer()
    
    # Create table data
    table_data = [
        ['Name', 'Property', 'Unit', 'Phone', 'Rent', 'Status']
    ]
    
    for tenant in tenants:
        property_name = db.query(Property.name).filter(Property.id == tenant.property_id).scalar()
        unit_number = db.query(Unit.unit_number).filter(Unit.id == tenant.unit_id).scalar()
        
        table_data.append([
            tenant.full_name,
            property_name or '-',
            unit_number or '-',
            tenant.phone,
            format_currency(tenant.base_rent),
            tenant.status.replace('_', ' ').title()
        ])
    
    pdf.add_table(table_data, col_widths=[1.5*72, 1.3*72, 0.7*72, 1.2*72, 1*72, 0.8*72])
    
    # Build PDF
    pdf_bytes = pdf.build()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=tenants_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    )


@router.get("/export/tenants/excel")
async def export_tenants_excel(
    property_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export tenants list as Excel"""
    
    # Query tenants
    query = db.query(Tenant).join(Property).filter(
        Property.landlord_id == current_user.id
    )
    
    if property_id:
        query = query.filter(Tenant.property_id == property_id)
    if status:
        query = query.filter(Tenant.status == status)
    
    tenants = query.order_by(Tenant.full_name).all()
    
    # Create Excel
    excel = ExcelExporter(filename="tenants.xlsx")
    
    headers = ['Name', 'Property', 'Unit', 'Phone', 'Email', 'ID Number', 
               'Monthly Rent', 'Deposit', 'Move-in Date', 'Status']
    
    data = []
    for tenant in tenants:
        property_name = db.query(Property.name).filter(Property.id == tenant.property_id).scalar()
        unit_number = db.query(Unit.unit_number).filter(Unit.id == tenant.unit_id).scalar()
        
        data.append([
            tenant.full_name,
            property_name or '-',
            unit_number or '-',
            tenant.phone,
            tenant.email or '-',
            tenant.id_number or '-',
            float(tenant.base_rent),
            float(tenant.security_deposit_amount),
            format_date(tenant.move_in_date),
            tenant.status.replace('_', ' ').title()
        ])
    
    excel.add_sheet('Tenants', headers, data)
    
    # Build Excel
    excel_bytes = excel.build()
    
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=tenants_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )


@router.get("/export/payments/pdf")
async def export_payments_pdf(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    property_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export payments report as PDF"""
    
    # Query payments
    query = db.query(Payment).join(Invoice).join(Property).filter(
        Property.landlord_id == current_user.id
    )
    
    if start_date:
        query = query.filter(Payment.trans_time >= start_date)
    if end_date:
        query = query.filter(Payment.trans_time <= end_date)
    if property_id:
        query = query.filter(Invoice.property_id == property_id)
    
    payments = query.order_by(Payment.trans_time.desc()).all()
    
    # Calculate totals
    total_amount = sum(float(p.amount) for p in payments)
    
    # Create PDF
    pdf = PDFExporter(title="Payments Report")
    pdf.add_title("Payments Report")
    
    date_range = "All Time"
    if start_date and end_date:
        date_range = f"{format_date(start_date)} to {format_date(end_date)}"
    elif start_date:
        date_range = f"From {format_date(start_date)}"
    elif end_date:
        date_range = f"Until {format_date(end_date)}"
    
    pdf.add_paragraph(f"Period: {date_range}")
    pdf.add_paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    pdf.add_spacer()
    
    # Summary
    pdf.add_key_value_pairs({
        'Total Payments': str(len(payments)),
        'Total Amount Collected': format_currency(total_amount),
    })
    pdf.add_spacer()
    
    # Payments table
    pdf.add_heading("Payment Details")
    table_data = [
        ['Date', 'Property', 'Tenant', 'Amount', 'Method', 'Reference']
    ]
    
    for payment in payments:
        invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()
        if invoice:
            property_name = db.query(Property.name).filter(Property.id == invoice.property_id).scalar()
            tenant = db.query(Tenant).filter(Tenant.id == invoice.tenant_id).first()
            
            table_data.append([
                format_date(payment.trans_time),
                property_name or '-',
                tenant.full_name if tenant else '-',
                format_currency(payment.amount),
                payment.payment_method.upper(),
                payment.trans_id or '-'
            ])
    
    pdf.add_table(table_data, col_widths=[0.9*72, 1.3*72, 1.3*72, 1*72, 0.8*72, 1.2*72])
    
    # Build PDF
    pdf_bytes = pdf.build()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=payments_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    )


@router.get("/export/payments/excel")
async def export_payments_excel(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    property_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export payments report as Excel"""
    
    # Query payments
    query = db.query(Payment).join(Invoice).join(Property).filter(
        Property.landlord_id == current_user.id
    )
    
    if start_date:
        query = query.filter(Payment.trans_time >= start_date)
    if end_date:
        query = query.filter(Payment.trans_time <= end_date)
    if property_id:
        query = query.filter(Invoice.property_id == property_id)
    
    payments = query.order_by(Payment.trans_time.desc()).all()
    
    # Create Excel
    excel = ExcelExporter(filename="payments.xlsx")
    
    headers = ['Payment Date', 'Property', 'Tenant', 'Amount', 'Payment Method', 
               'Transaction ID', 'Invoice Number', 'Status']
    
    data = []
    for payment in payments:
        invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()
        if invoice:
            property_name = db.query(Property.name).filter(Property.id == invoice.property_id).scalar()
            tenant = db.query(Tenant).filter(Tenant.id == invoice.tenant_id).first()
            
            data.append([
                format_date(payment.trans_time),
                property_name or '-',
                tenant.full_name if tenant else '-',
                float(payment.amount),
                payment.payment_method.upper(),
                payment.trans_id or '-',
                invoice.invoice_number or '-',
                'Matched' if payment.invoice_id else 'Unmatched'
            ])
    
    excel.add_sheet('Payments', headers, data)
    
    # Build Excel
    excel_bytes = excel.build()
    
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=payments_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )


@router.get("/export/invoices/pdf")
async def export_invoices_pdf(
    status: Optional[str] = Query(None),
    property_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export invoices as PDF"""
    
    # Query invoices
    query = db.query(Invoice).join(Property).filter(
        Property.landlord_id == current_user.id
    )
    
    if status:
        query = query.filter(Invoice.status == status)
    if property_id:
        query = query.filter(Invoice.property_id == property_id)
    
    invoices = query.order_by(Invoice.due_date.desc()).all()
    
    # Calculate totals - use amount and paid_amount
    total_amount = sum(float(i.amount) for i in invoices)
    total_paid = sum(float(i.paid_amount) for i in invoices)
    total_balance = sum(float(i.amount) - float(i.paid_amount) for i in invoices)
    
    # Create PDF
    pdf = PDFExporter(title="Invoices Report")
    pdf.add_title("Invoices Report")
    pdf.add_paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    pdf.add_spacer()
    
    # Summary
    pdf.add_key_value_pairs({
        'Total Invoices': str(len(invoices)),
        'Total Invoiced': format_currency(total_amount),
        'Total Paid': format_currency(total_paid),
        'Total Outstanding': format_currency(total_balance),
    })
    pdf.add_spacer()
    
    # Invoices table
    pdf.add_heading("Invoice Details")
    table_data = [
        ['Invoice #', 'Tenant', 'Due Date', 'Amount', 'Paid', 'Balance', 'Status']
    ]
    
    for invoice in invoices:
        tenant = db.query(Tenant).filter(Tenant.id == invoice.tenant_id).first()
        
        table_data.append([
            invoice.invoice_number or '-',
            tenant.full_name if tenant else '-',
            format_date(invoice.due_date),
            format_currency(invoice.amount),
            format_currency(invoice.paid_amount),
            format_currency(float(invoice.amount) - float(invoice.paid_amount)),
            invoice.status.replace('_', ' ').title()
        ])
    
    pdf.add_table(table_data, col_widths=[0.9*72, 1.3*72, 0.9*72, 0.9*72, 0.9*72, 0.9*72, 0.8*72])
    
    # Build PDF
    pdf_bytes = pdf.build()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoices_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    )


@router.get("/export/invoices/excel")
async def export_invoices_excel(
    status: Optional[str] = Query(None),
    property_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export invoices as Excel"""
    
    # Query invoices
    query = db.query(Invoice).join(Property).filter(
        Property.landlord_id == current_user.id
    )
    
    if status:
        query = query.filter(Invoice.status == status)
    if property_id:
        query = query.filter(Invoice.property_id == property_id)
    
    invoices = query.order_by(Invoice.due_date.desc()).all()
    
    # Create Excel
    excel = ExcelExporter(filename="invoices.xlsx")
    
    headers = ['Invoice Number', 'Property', 'Unit', 'Tenant', 'Due Date', 
               'Amount', 'Paid', 'Balance', 'Status']
    
    data = []
    for invoice in invoices:
        property_name = db.query(Property.name).filter(Property.id == invoice.property_id).scalar()
        unit = db.query(Unit).filter(Unit.id == invoice.unit_id).first()
        tenant = db.query(Tenant).filter(Tenant.id == invoice.tenant_id).first()
        
        data.append([
            invoice.invoice_number or '-',
            property_name or '-',
            unit.unit_number if unit else '-',
            tenant.full_name if tenant else '-',
            format_date(invoice.due_date),
            float(invoice.amount),
            float(invoice.paid_amount),
            float(invoice.amount) - float(invoice.paid_amount),
            invoice.status.replace('_', ' ').title()
        ])
    
    excel.add_sheet('Invoices', headers, data)
    
    # Build Excel
    excel_bytes = excel.build()
    
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=invoices_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )