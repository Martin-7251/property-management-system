"""
Email Service
Send email notifications using SendGrid
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging
from typing import Optional
from datetime import date
from decimal import Decimal

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        if settings.EMAIL_ENABLED:
            self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            self.from_email = Email(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME)
        else:
            self.client = None
            logger.warning("Email is disabled in settings")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> dict:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            plain_content: Plain text fallback
            
        Returns:
            Dictionary with result
        """
        if not settings.EMAIL_ENABLED:
            logger.info(f"Email disabled. Would have sent to {to_email}: {subject}")
            return {"success": False, "message": "Email is disabled"}
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if plain_content:
                message.add_content(Content("text/plain", plain_content))
            
            response = self.client.send(message)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return {
                "success": True,
                "status_code": response.status_code
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_payment_receipt(
        self,
        tenant_name: str,
        tenant_email: str,
        trans_id: str,
        amount: Decimal,
        payment_date: date,
        invoice_number: str,
        unit_number: str,
        balance: Decimal
    ) -> dict:
        """
        Send payment receipt email.
        
        Args:
            tenant_name: Tenant's full name
            tenant_email: Tenant's email
            trans_id: Transaction ID
            amount: Payment amount
            payment_date: Date of payment
            invoice_number: Invoice number
            unit_number: Unit number
            balance: Remaining balance
        """
        subject = f"Payment Receipt - {trans_id}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #4CAF50; color: white; padding: 20px; text-align: center;">
                <h1>Payment Received</h1>
            </div>
            
            <div style="padding: 20px; background-color: #f9f9f9;">
                <p>Dear {tenant_name},</p>
                
                <p>Thank you for your payment. Here are the details:</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f2f2f2;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Transaction ID</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{trans_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Amount Paid</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">KES {amount:,.2f}</td>
                    </tr>
                    <tr style="background-color: #f2f2f2;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Date</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{payment_date.strftime('%d %B %Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Invoice</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{invoice_number}</td>
                    </tr>
                    <tr style="background-color: #f2f2f2;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Unit</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{unit_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Balance</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd; {'color: green;' if balance <= 0 else ''}">
                            KES {balance:,.2f} {'✓ PAID' if balance <= 0 else ''}
                        </td>
                    </tr>
                </table>
                
                <p>Keep this receipt for your records.</p>
                
                <p>Thank you for your prompt payment!</p>
                
                <p>Best regards,<br>
                Property Management Team</p>
            </div>
            
            <div style="background-color: #333; color: white; padding: 10px; text-align: center; font-size: 12px;">
                <p>This is an automated email. Please do not reply.</p>
            </div>
        </body>
        </html>
        """
        
        plain_content = f"""
        Payment Receipt
        
        Dear {tenant_name},
        
        Payment received successfully!
        
        Transaction ID: {trans_id}
        Amount Paid: KES {amount:,.2f}
        Date: {payment_date.strftime('%d %B %Y')}
        Invoice: {invoice_number}
        Unit: {unit_number}
        Balance: KES {balance:,.2f}
        
        Thank you!
        """
        
        return self.send_email(tenant_email, subject, html_content, plain_content)
    
    def send_invoice_notification(
        self,
        tenant_name: str,
        tenant_email: str,
        invoice_number: str,
        amount: Decimal,
        due_date: date,
        invoice_type: str,
        unit_number: str
    ) -> dict:
        """
        Send invoice notification email.
        """
        invoice_type_text = "Security Deposit" if invoice_type == "security_deposit" else "Monthly Rent"
        
        subject = f"New Invoice - {invoice_number}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #2196F3; color: white; padding: 20px; text-align: center;">
                <h1>New Invoice</h1>
            </div>
            
            <div style="padding: 20px;">
                <p>Dear {tenant_name},</p>
                
                <p>A new {invoice_type_text} invoice has been generated for your unit.</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f2f2f2;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Invoice Number</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{invoice_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Type</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{invoice_type_text}</td>
                    </tr>
                    <tr style="background-color: #f2f2f2;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Unit</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{unit_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Amount Due</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 18px; font-weight: bold;">
                            KES {amount:,.2f}
                        </td>
                    </tr>
                    <tr style="background-color: #fff3cd;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Due Date</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">
                            {due_date.strftime('%d %B %Y')}
                        </td>
                    </tr>
                </table>
                
                <p><strong>Payment Instructions:</strong></p>
                <ol>
                    <li>Go to M-Pesa on your phone</li>
                    <li>Select Lipa na M-Pesa → Pay Bill</li>
                    <li>Enter Business Number</li>
                    <li>Account Number: <strong>{unit_number}</strong></li>
                    <li>Amount: <strong>{amount:,.2f}</strong></li>
                    <li>Enter your M-Pesa PIN and confirm</li>
                </ol>
                
                <p style="color: red;">Please pay before {due_date.strftime('%d %B %Y')} to avoid late fees.</p>
                
                <p>Best regards,<br>
                Property Management Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(tenant_email, subject, html_content)


# Global email service instance
email_service = EmailService()