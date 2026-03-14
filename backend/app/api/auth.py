"""
Authentication API Routes
Endpoints for user registration, login, and profile
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    validate_password_strength,
)
from app.api.deps import get_current_user
from pydantic import BaseModel

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new landlord account.
    
    **Requirements:**
    - Unique email address
    - Password minimum 8 characters
    - Valid phone number in E.164 format (+254712345678)
    
    **Returns:**
    - User object with ID and timestamps
    - Password is NOT returned
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Create new user
    db_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role="landlord",  # All registered users are landlords
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
def login(
    username: str = Form(...),  # OAuth2 expects 'username' (use email here)
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Login with email and password to get JWT token.
    
    **Important:** Enter your email in the 'username' field.
    
    **How to use the token after login:**
    1. Copy the `access_token` from the response
    2. Click the "Authorize" button (lock icon) at the top
    3. Paste ONLY the token (without "Bearer")
    4. Click "Authorize"
    5. The lock icon will close - you're now authenticated!
    6. Now you can test protected endpoints like /api/auth/me
    
    **Token expires in 24 hours.**
    """
    # Find user by email (username field contains email)
    user = db.query(User).filter(User.email == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current logged-in user's information.
    
    **Requires authentication** (JWT token).
    
    **How to test:**
    1. Login to get a token
    2. Click "Authorize" and add token
    3. Execute this endpoint
    """
    return current_user


@router.get("/test-auth")
def test_auth(current_user: User = Depends(get_current_user)):
    """
    Test endpoint to verify authentication is working.
    
    **Requires authentication.**
    
    Returns a simple message with your email if token is valid.
    """
    return {
        "message": "Authentication successful!",
        "your_email": current_user.email,
        "your_name": current_user.full_name,
        "your_role": current_user.role
    }


@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for the current logged-in user.
    
    **Requirements:**
    - Must provide correct current password
    - New password must be at least 8 characters
    - New password must be different from current password
    
    **Returns:**
    - Success message
    """
    # Verify old password
    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    is_valid, error_message = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Don't allow same password
    if verify_password(request.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(request.new_password)
    db.commit()
    
    return {
        "message": "Password changed successfully",
        "success": True
    }