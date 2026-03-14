"""
API Dependencies
Reusable dependencies for FastAPI endpoints
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

# OAuth2 scheme for token authentication
# tokenUrl is the endpoint where users get tokens (will be /api/auth/login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    This dependency can be used in any endpoint that requires authentication:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object of authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Get user ID from token
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


def get_current_active_landlord(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they are a landlord.
    
    Use this for endpoints that only landlords can access.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if user is a landlord
        
    Raises:
        HTTPException: If user is not a landlord
    """
    if current_user.role != "landlord":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Landlord role required."
        )
    return current_user


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they are an admin.
    
    Use this for admin-only endpoints.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if user is an admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user