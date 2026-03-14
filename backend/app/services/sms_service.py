"""
SMS Notification Service
Send SMS notifications using Africa's Talking API
"""

import africastalking
import logging
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from app.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS notifications"""
    
    def __init__(self):
        # Initialize Africa's Talking
        if settings.SMS_ENABLED:
            africastalking.initialize(
                username=settings.AFRICASTALKING_USERNAME,
                api_key=settings.AFRICASTALKING_API_KEY
            )
            self.sms = africastalking.SMS
        else:
            self.sms = None
            logger.warning("SMS is disabled in settings")
    
    def send_sms(self, phone: str, message: str) -> dict:
        """
        Send a single SMS.
        
        Args:
            phone: Phone number in E.164 format (+254722111111)
            message: SMS message text
            
        Returns:
            Dictionary with result
        """
        if not settings.SMS_ENABLED:
            logger.info(f"SMS disabled. Would have sent to {phone}: {message}")
            return {"success": False, "message": "SMS is disabled"}
        
        try:
            response = self.sms.send(
                message=message,
                recipients=[phone],
                sender_id=settings.AFRICASTALKING_FROM
            )
            
            logger.info(f"SMS sent to {phone}: {response}")
            return {
                "success": True,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_invoice_created(
        self,
        tenant_name: str,
        phone: str,
        invoice_number: str,
        amount: Decimal,
        due_date: date,
        invoice_type: str
    ) -> dict:
        """
        Send notification when invoice is created.
        
        Args:
            tenant_name: Tenant's full name
            phone: Tenant's phone number
            invoice_number: Invoice number
            amount: Invoice amount
            due_date: Payment due date
            invoice_type: monthly_rent or security_deposit
        """
        invoice_type_text = "Security Deposit" if invoice_type == "security_deposit" else "Rent"
        
        message = (
            f"Hello {tenant_name},\n"
            f"New {invoice_type_text} invoice #{invoice_number} created.\n"
            f"Amount: KES {amount:,.2f}\n"
            f"Due: {due_date.strftime('%d %b %Y')}\n"
            f"Pay via M-Pesa to avoid late fees."
        )
        
        return self.send_sms(phone, message)
    
    def send_payment_received(
        self,
        tenant_name: str,
        phone: str,
        amount: Decimal,
        invoice_number: str,
        balance: Decimal
    ) -> dict:
        """
        Send notification when payment is received.
        
        Args:
            tenant_name: Tenant's full name
            phone: Tenant's phone number
            amount: Payment amount received
            invoice_number: Invoice number
            balance: Remaining balance (0 if fully paid)
        """
        if balance <= 0:
            message = (
                f"Hello {tenant_name},\n"
                f"Payment of KES {amount:,.2f} received.\n"
                f"Invoice #{invoice_number} is FULLY PAID.\n"
                f"Thank you!"
            )
        else:
            message = (
                f"Hello {tenant_name},\n"
                f"Payment of KES {amount:,.2f} received.\n"
                f"Invoice #{invoice_number}\n"
                f"Balance: KES {balance:,.2f}"
            )
        
        return self.send_sms(phone, message)
    
    def send_payment_reminder(
        self,
        tenant_name: str,
        phone: str,
        invoice_number: str,
        amount: Decimal,
        due_date: date,
        days_until_due: int
    ) -> dict:
        """
        Send payment reminder.
        
        Args:
            tenant_name: Tenant's full name
            phone: Tenant's phone number
            invoice_number: Invoice number
            amount: Amount due
            due_date: Payment due date
            days_until_due: Days remaining until due
        """
        if days_until_due > 0:
            message = (
                f"Hello {tenant_name},\n"
                f"Reminder: Invoice #{invoice_number}\n"
                f"Amount: KES {amount:,.2f}\n"
                f"Due in {days_until_due} day(s) ({due_date.strftime('%d %b')})\n"
                f"Please pay to avoid late fees."
            )
        else:
            message = (
                f"Hello {tenant_name},\n"
                f"URGENT: Invoice #{invoice_number}\n"
                f"Amount: KES {amount:,.2f}\n"
                f"DUE TODAY ({due_date.strftime('%d %b')})\n"
                f"Please pay immediately."
            )
        
        return self.send_sms(phone, message)
    
    def send_overdue_notice(
        self,
        tenant_name: str,
        phone: str,
        invoice_number: str,
        amount: Decimal,
        days_overdue: int
    ) -> dict:
        """
        Send overdue payment notice.
        
        Args:
            tenant_name: Tenant's full name
            phone: Tenant's phone number
            invoice_number: Invoice number
            amount: Amount overdue
            days_overdue: Days past due
        """
        message = (
            f"Hello {tenant_name},\n"
            f"OVERDUE: Invoice #{invoice_number}\n"
            f"Amount: KES {amount:,.2f}\n"
            f"{days_overdue} day(s) overdue.\n"
            f"Please pay immediately to avoid further action."
        )
        
        return self.send_sms(phone, message)
    
    def send_welcome_message(
        self,
        tenant_name: str,
        phone: str,
        unit_number: str,
        move_in_date: date
    ) -> dict:
        """
        Send welcome message to new tenant.
        
        Args:
            tenant_name: Tenant's full name
            phone: Tenant's phone number
            unit_number: Unit number
            move_in_date: Move-in date
        """
        message = (
            f"Welcome {tenant_name}!\n"
            f"You've been registered for Unit {unit_number}.\n"
            f"Move-in: {move_in_date.strftime('%d %b %Y')}\n"
            f"You will receive payment reminders via SMS.\n"
            f"Thank you for choosing us!"
        )
        
        return self.send_sms(phone, message)


# Global SMS service instance
sms_service = SMSService()