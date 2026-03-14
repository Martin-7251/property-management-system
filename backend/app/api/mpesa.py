"""
M-Pesa API Routes
Webhook endpoints for M-Pesa payment callbacks
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
import logging

from app.database import get_db
from app.models.payment import Payment
from app.models.mpesa_config import MpesaConfig
from app.services.payment_matcher import PaymentMatcher

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/mpesa/validation")
async def mpesa_validation(request: Request, db: Session = Depends(get_db)):
    """
    M-Pesa validation callback.
    
    Called by M-Pesa to validate a payment before processing.
    
    Return:
    - ResultCode 0 = Accept payment
    - ResultCode 1 = Reject payment
    """
    try:
        data = await request.json()
        logger.info(f"M-Pesa validation request: {data}")
        
        # You can add validation logic here
        # For now, accept all payments
        
        return {
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }
        
    except Exception as e:
        logger.error(f"M-Pesa validation error: {e}")
        return {
            "ResultCode": 1,
            "ResultDesc": "Rejected"
        }


@router.post("/mpesa/confirmation")
async def mpesa_confirmation(request: Request, db: Session = Depends(get_db)):
    """
    M-Pesa confirmation callback.
    
    Called by M-Pesa after a successful payment.
    Creates payment record and attempts to match with invoice.
    
    Expected payload from M-Pesa:
    {
        "TransactionType": "Pay Bill",
        "TransID": "SAF123...",
        "TransTime": "20260204153000",
        "TransAmount": "25000.00",
        "BusinessShortCode": "600100",
        "BillRefNumber": "A1",
        "MSISDN": "254722111111",
        "FirstName": "Alice",
        "MiddleName": "",
        "LastName": "Wanjiku"
    }
    """
    try:
        data = await request.json()
        logger.info(f"M-Pesa confirmation received: {data}")
        
        # Extract M-Pesa data
        trans_id = data.get("TransID")
        trans_amount = data.get("TransAmount")
        trans_time_str = data.get("TransTime")  # Format: YYYYMMDDHHmmss
        business_shortcode = data.get("BusinessShortCode")
        bill_ref_number = data.get("BillRefNumber")
        msisdn = data.get("MSISDN")
        first_name = data.get("FirstName", "")
        middle_name = data.get("MiddleName", "")
        last_name = data.get("LastName", "")
        
        # Check if payment already exists (prevent duplicates)
        existing = db.query(Payment).filter(Payment.trans_id == trans_id).first()
        if existing:
            logger.warning(f"Duplicate payment ignored: {trans_id}")
            return {
                "ResultCode": 0,
                "ResultDesc": "Duplicate transaction"
            }
        
        # Parse transaction time
        try:
            trans_time = datetime.strptime(trans_time_str, "%Y%m%d%H%M%S")
        except:
            trans_time = datetime.now()
        
        # Find property by paybill shortcode
        mpesa_config = db.query(MpesaConfig).filter(
            MpesaConfig.paybill_shortcode == business_shortcode
        ).first()
        
        property_id = mpesa_config.property_id if mpesa_config else None
        
        # Create payment record
        payment = Payment(
            trans_id=trans_id,
            amount=Decimal(str(trans_amount)),
            msisdn=msisdn,
            paybill_shortcode=business_shortcode,
            bill_ref_number=bill_ref_number,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            trans_time=trans_time,
            payment_method="mpesa",
            status="unmatched",
            property_id=property_id,
            raw_payload=data
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Attempt to match payment with invoice
        matcher = PaymentMatcher(db)
        matched = matcher.match_payment(payment)
        
        if matched:
            logger.info(f"Payment {trans_id} automatically matched!")
        else:
            logger.warning(f"Payment {trans_id} could not be matched automatically")
        
        return {
            "ResultCode": 0,
            "ResultDesc": "Payment received successfully"
        }
        
    except Exception as e:
        logger.error(f"M-Pesa confirmation error: {e}")
        db.rollback()
        return {
            "ResultCode": 1,
            "ResultDesc": f"Error: {str(e)}"
        }


@router.post("/mpesa/test-payment")
def test_payment(
    shortcode: str,
    amount: float,
    unit_number: str,
    phone: str = "254722111111",
    db: Session = Depends(get_db)
):
    """
    Test endpoint to simulate M-Pesa payment.
    
    Use this for testing without actual M-Pesa integration.
    
    Examples:
    - unit_number: "A1" (for rent)
    - unit_number: "A1-DEP" (for security deposit)
    """
    try:
        # Find property by shortcode
        mpesa_config = db.query(MpesaConfig).filter(
            MpesaConfig.paybill_shortcode == shortcode
        ).first()
        
        if not mpesa_config:
            return {"error": "Paybill not found"}
        
        # Create fake transaction ID
        import random
        trans_id = f"TEST{random.randint(100000, 999999)}"
        
        # Create payment
        payment = Payment(
            trans_id=trans_id,
            amount=Decimal(str(amount)),
            msisdn=phone,
            paybill_shortcode=shortcode,
            bill_ref_number=unit_number,
            first_name="Test",
            middle_name="",
            last_name="User",
            trans_time=datetime.now(),
            payment_method="mpesa",
            status="unmatched",
            property_id=mpesa_config.property_id,
            raw_payload={"test": True}
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Match payment
        matcher = PaymentMatcher(db)
        matched = matcher.match_payment(payment)
        
        return {
            "success": True,
            "trans_id": trans_id,
            "matched": matched,
            "payment_id": str(payment.id)
        }
        
    except Exception as e:
        logger.error(f"Test payment error: {e}")
        db.rollback()
        return {"error": str(e)}