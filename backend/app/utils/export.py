"""
Export utilities for generating PDF and Excel reports
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import xlsxwriter
from io import BytesIO
from typing import List, Dict, Any


class PDFExporter:
    """Generate PDF reports"""
    
    def __init__(self, title: str, author: str = "Property Management System"):
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        self.title = title
        self.author = author
        self.styles = getSampleStyleSheet()
        self.elements = []
        
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
        ))
        
    def add_title(self, text: str):
        """Add report title"""
        self.elements.append(Paragraph(text, self.styles['CustomTitle']))
        self.elements.append(Spacer(1, 12))
        
    def add_heading(self, text: str):
        """Add section heading"""
        self.elements.append(Paragraph(text, self.styles['CustomHeading']))
        self.elements.append(Spacer(1, 6))
        
    def add_paragraph(self, text: str):
        """Add paragraph text"""
        self.elements.append(Paragraph(text, self.styles['Normal']))
        self.elements.append(Spacer(1, 12))
        
    def add_table(self, data: List[List[str]], col_widths: List[float] = None):
        """
        Add table to PDF
        data: List of rows, first row is header
        col_widths: List of column widths in inches
        """
        if not data:
            return
            
        # Create table
        table = Table(data, colWidths=col_widths)
        
        # Style
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.elements.append(table)
        self.elements.append(Spacer(1, 12))
        
    def add_key_value_pairs(self, pairs: Dict[str, str]):
        """Add key-value pairs as table"""
        data = [[k, v] for k, v in pairs.items()]
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        self.elements.append(table)
        self.elements.append(Spacer(1, 12))
        
    def add_spacer(self, height: float = 0.2):
        """Add vertical space"""
        self.elements.append(Spacer(1, height * inch))
        
    def build(self) -> bytes:
        """Build and return PDF bytes"""
        # Add metadata
        self.doc.title = self.title
        self.doc.author = self.author
        
        # Build PDF
        self.doc.build(self.elements)
        
        # Get bytes
        pdf_bytes = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf_bytes


class ExcelExporter:
    """Generate Excel spreadsheets"""
    
    def __init__(self, filename: str):
        self.buffer = BytesIO()
        self.workbook = xlsxwriter.Workbook(self.buffer, {'in_memory': True})
        self.filename = filename
        
        # Define formats
        self.header_format = self.workbook.add_format({
            'bold': True,
            'bg_color': '#1e40af',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        self.currency_format = self.workbook.add_format({
            'num_format': 'KES #,##0.00',
            'border': 1
        })
        
        self.date_format = self.workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'border': 1
        })
        
        self.cell_format = self.workbook.add_format({
            'border': 1,
            'valign': 'vcenter'
        })
        
        self.title_format = self.workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': '#1e40af'
        })
        
    def add_sheet(
        self, 
        sheet_name: str, 
        headers: List[str], 
        data: List[List[Any]],
        col_widths: List[int] = None
    ):
        """
        Add worksheet with data
        sheet_name: Name of the sheet
        headers: List of column headers
        data: List of rows
        col_widths: List of column widths (optional)
        """
        worksheet = self.workbook.add_worksheet(sheet_name)
        
        # Write headers
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, self.header_format)
        
        # Write data
        for row_idx, row in enumerate(data, start=1):
            for col_idx, value in enumerate(row):
                # Auto-detect format
                if isinstance(value, (int, float)):
                    if col_idx > 0 and any(keyword in headers[col_idx].lower() 
                                          for keyword in ['rent', 'amount', 'price', 'cost', 'total', 'paid', 'balance']):
                        worksheet.write(row_idx, col_idx, value, self.currency_format)
                    else:
                        worksheet.write(row_idx, col_idx, value, self.cell_format)
                elif isinstance(value, str) and any(keyword in headers[col_idx].lower() 
                                                   for keyword in ['date']):
                    worksheet.write(row_idx, col_idx, value, self.date_format)
                else:
                    worksheet.write(row_idx, col_idx, value, self.cell_format)
        
        # Set column widths
        if col_widths:
            for col, width in enumerate(col_widths):
                worksheet.set_column(col, col, width)
        else:
            # Auto-size columns
            for col, header in enumerate(headers):
                max_width = len(header)
                for row in data:
                    if col < len(row):
                        max_width = max(max_width, len(str(row[col])))
                worksheet.set_column(col, col, min(max_width + 2, 50))
        
        # Freeze header row
        worksheet.freeze_panes(1, 0)
        
    def build(self) -> bytes:
        """Build and return Excel bytes"""
        self.workbook.close()
        excel_bytes = self.buffer.getvalue()
        self.buffer.close()
        return excel_bytes


def format_currency(amount: float) -> str:
    """Format number as KES currency"""
    return f"KES {amount:,.2f}"


def format_date(date_obj) -> str:
    """Format date object to string"""
    if date_obj:
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime('%Y-%m-%d')
    return '-'