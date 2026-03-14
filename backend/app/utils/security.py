"""
Security Utilities - FIXED for bcrypt 72-byte limit
Password hashing and JWT token management
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Bcrypt has a 72-byte limit, so we truncate if necessary.
    
    Args:
        plain_password: The plain text password from user
        hashed_password: The hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    # Bcrypt has a 72 byte limit, truncate if necessary
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Bcrypt has a 72-byte limit, so we truncate if necessary.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    # Bcrypt has a 72 byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing user data (usually {"sub": user_id})
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary with token data if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def validate_password_strength(password: str) -> tuple:
    """
    Validate password meets minimum requirements.
    
    Args:
        password: Plain text password
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long"
    
    # Warn if password is too long for bcrypt
    if len(password.encode('utf-8')) > 72:
        return False, "Password is too long (max 72 bytes)"
    
    # Add more checks if needed (optional)
    # Uncomment these for stricter password requirements:
    
    # if not any(char.isdigit() for char in password):
    #     return False, "Password must contain at least one number"
    
    # if not any(char.isupper() for char in password):
    #     return False, "Password must contain at least one uppercase letter"
    
    # if not any(char.islower() for char in password):
    #     return False, "Password must contain at least one lowercase letter"
    
    return True, ""