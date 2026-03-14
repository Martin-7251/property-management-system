"""
Configuration Module

Compatible with:
- Python 3.11
- FastAPI 0.95.x
- Pydantic v1.10.x
"""

from typing import List, Optional
from pydantic import BaseSettings
import secrets


class Settings(BaseSettings):
    # ───────────────────────────────
    # APPLICATION
    # ───────────────────────────────
    APP_NAME: str = "Property Management API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ───────────────────────────────
    # DATABASE
    # ───────────────────────────────
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # ───────────────────────────────
    # SECURITY
    # ───────────────────────────────
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    MIN_PASSWORD_LENGTH: int = 8

    # ───────────────────────────────
    # API
    # ───────────────────────────────
    API_V1_PREFIX: str = "/api"
    BACKEND_CORS_ORIGINS: str = ""

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """
        Returns CORS origins as a list.
        Expected env format:
        BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
        """
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    # ───────────────────────────────
    # M-PESA
    # ───────────────────────────────
    MPESA_ENVIRONMENT: str = "sandbox"
    MPESA_CONSUMER_KEY: str = ""
    MPESA_CONSUMER_SECRET: str = ""
    MPESA_PASSKEY: str = ""
    MPESA_SHORTCODE: str = ""
    MPESA_CALLBACK_BASE_URL: str = "http://localhost:8000"

    @property
    def MPESA_BASE_URL(self) -> str:
        return (
            "https://api.safaricom.co.ke"
            if self.MPESA_ENVIRONMENT == "production"
            else "https://sandbox.safaricom.co.ke"
        )

    @property
    def MPESA_VALIDATION_URL(self) -> str:
        return f"{self.MPESA_CALLBACK_BASE_URL}{self.API_V1_PREFIX}/mpesa/validation"

    @property
    def MPESA_CONFIRMATION_URL(self) -> str:
        return f"{self.MPESA_CALLBACK_BASE_URL}{self.API_V1_PREFIX}/mpesa/confirmation"

    # ───────────────────────────────
    # SMS
    # ───────────────────────────────
    AFRICASTALKING_USERNAME: str = "sandbox"
    AFRICASTALKING_API_KEY: str = ""
    AFRICASTALKING_FROM: str = "PROPMGMT"
    SMS_ENABLED: bool = False
    SMS_COST_PER_MESSAGE: float = 0.80

    # ───────────────────────────────
    # EMAIL
    # ───────────────────────────────
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@example.com"
    SENDGRID_FROM_NAME: str = "Property Manager"
    EMAIL_ENABLED: bool = False

    # ───────────────────────────────
    # NOTIFICATIONS
    # ───────────────────────────────
    SEND_SMS_NOTIFICATIONS: bool = False
    SEND_EMAIL_NOTIFICATIONS: bool = False
    PAYMENT_REMINDER_DAY_1: int = 5
    PAYMENT_REMINDER_DAY_2: int = 9

    # ───────────────────────────────
    # CRON / BACKGROUND JOBS
    # ───────────────────────────────
    INVOICE_GENERATION_ENABLED: bool = True
    PAYMENT_REMINDERS_ENABLED: bool = True
    OVERDUE_CHECK_ENABLED: bool = True

    # ───────────────────────────────
    # FILE UPLOADS
    # ───────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx"
    ]

    # ───────────────────────────────
    # LOGGING
    # ───────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # ───────────────────────────────
    # RATE LIMITING
    # ───────────────────────────────
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # ───────────────────────────────
    # ENCRYPTION
    # ───────────────────────────────
    ENCRYPTION_KEY: Optional[str] = None

    # ───────────────────────────────
    # TESTING
    # ───────────────────────────────
    TEST_DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
