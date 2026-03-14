"""
M-Pesa Service
Handles M-Pesa API integration (Daraja API)
"""

import requests
import base64
from datetime import datetime
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class MpesaService:
    """Service for M-Pesa API integration"""
    
    def __init__(self, consumer_key: str, consumer_secret: str, environment: str = "sandbox"):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.environment = environment
        self.base_url = settings.MPESA_BASE_URL if environment == "production" else "https://sandbox.safaricom.co.ke"
    
    def get_access_token(self) -> Optional[str]:
        """
        Get OAuth access token from M-Pesa API.
        
        Returns:
            Access token string or None if failed
        """
        try:
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            
            # Create basic auth header
            auth_string = f"{self.consumer_key}:{self.consumer_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_base64}"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("access_token")
            
        except Exception as e:
            logger.error(f"Failed to get M-Pesa access token: {e}")
            return None
    
    def register_urls(
        self,
        shortcode: str,
        validation_url: str,
        confirmation_url: str
    ) -> bool:
        """
        Register validation and confirmation URLs with M-Pesa.
        
        This tells M-Pesa where to send payment notifications.
        
        Args:
            shortcode: Paybill/Till number
            validation_url: URL for validation callback
            confirmation_url: URL for confirmation callback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return False
            
            url = f"{self.base_url}/mpesa/c2b/v1/registerurl"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "ShortCode": shortcode,
                "ResponseType": "Completed",  # or "Cancelled"
                "ConfirmationURL": confirmation_url,
                "ValidationURL": validation_url
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            logger.info(f"M-Pesa URLs registered successfully for {shortcode}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register M-Pesa URLs: {e}")
            return False
    
    def simulate_c2b_payment(
        self,
        shortcode: str,
        amount: float,
        msisdn: str,
        bill_ref_number: str
    ) -> Optional[dict]:
        """
        Simulate a C2B payment (for testing in sandbox).
        
        Args:
            shortcode: Paybill/Till number
            amount: Payment amount
            msisdn: Customer phone number (254...)
            bill_ref_number: Account reference (unit number)
            
        Returns:
            Response data or None if failed
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            url = f"{self.base_url}/mpesa/c2b/v1/simulate"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "ShortCode": shortcode,
                "CommandID": "CustomerPayBillOnline",
                "Amount": str(amount),
                "Msisdn": msisdn,
                "BillRefNumber": bill_ref_number
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to simulate M-Pesa payment: {e}")
            return None


def get_mpesa_service(consumer_key: str, consumer_secret: str, environment: str = "sandbox") -> MpesaService:
    """Factory function to create M-Pesa service instance"""
    return MpesaService(consumer_key, consumer_secret, environment)