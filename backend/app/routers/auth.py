from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import re

from app.database import get_db
from app.models import User, UserStatus, VerificationCodeType
from app.utils.password import hash_password, verify_password, validate_password_strength
from app.utils.jwt import create_access_token
from app.services.verification_service import VerificationService
from app.dependencies.auth import get_current_user

router = APIRouter()

# Pydantic schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class RequestEmailChangeRequest(BaseModel):
    new_email: EmailStr

class VerifyEmailChangeRequest(BaseModel):
    new_email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    status: str
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

# Helper function to validate email format (additional validation)
def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Registration endpoints
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account
    - Validates email and password strength
    - Creates user with unverified status
    - Sends verification code via email
    """
    # Validate password strength
    is_valid, message = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already registered"
        )
    
    # Create new user
    hashed_password = hash_password(request.password)
    new_user = User(
        email=request.email,
        password_hash=hashed_password,
        status=UserStatus.UNVERIFIED
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send verification email
    verification_service = VerificationService()
    success, msg = verification_service.send_verification_email(
        db, request.email, VerificationCodeType.EMAIL_VERIFICATION
    )
    
    if not success:
        # User created but email failed - still return success
        return {
            "message": "注册成功，但验证码发送失败，请稍后重试",
            "email": request.email
        }
    
    return {
        "message": "注册成功！请查收邮件并输入验证码",
        "email": request.email
    }

@router.post("/verify-email", response_model=AuthResponse)
def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """
    Verify email with verification code
    - Validates the code
    - Activates the user account
    - Returns authentication token
    """
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.status == UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already activated"
        )
    
    # Verify code
    verification_service = VerificationService()
    is_valid, message = verification_service.verify_code(
        db, request.email, request.code, VerificationCodeType.EMAIL_VERIFICATION
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Activate user
    user.status = UserStatus.ACTIVE
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Generate token
    token = create_access_token({"user_id": user.id})
    
    return {
        "token": token,
        "user": UserResponse.from_orm(user)
    }

@router.post("/resend-verification")
def resend_verification(request: ResendVerificationRequest, db: Session = Depends(get_db)):
    """
    Resend verification code to email
    """
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not (security)
        return {"message": "如果该邮箱已注册，验证码将发送到邮箱"}
    
    if user.status == UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already activated，无需验证"
        )
    
    # Send verification email
    verification_service = VerificationService()
    success, msg = verification_service.send_verification_email(
        db, request.email, VerificationCodeType.EMAIL_VERIFICATION
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=msg
        )
    
    return {"message": "验证码已重新发送"}

# Login endpoints
@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password
    - Validates credentials
    - Checks account status
    - Returns authentication token
    """
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check account status
    if user.status == UserStatus.UNVERIFIED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified. Please verify your email first"
        )
    elif user.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been suspended"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Generate token
    token = create_access_token(
        {"user_id": user.id},
        remember_me=request.remember_me
    )
    
    return {
        "token": token,
        "user": UserResponse.from_orm(user)
    }

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout (mainly for consistency, token invalidation happens on client)
    """
    return {"message": "登出成功"}

# Password management endpoints
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request password reset code
    - Sends verification code to email
    """
    # Check if user exists (don't reveal for security)
    user = db.query(User).filter(User.email == request.email).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "如果该邮箱已注册，重置验证码将发送到邮箱"}
    
    # Send reset code
    verification_service = VerificationService()
    success, msg = verification_service.send_verification_email(
        db, request.email, VerificationCodeType.PASSWORD_RESET
    )
    
    return {"message": "如果该邮箱已注册，重置验证码将发送到邮箱"}

@router.post("/reset-password", response_model=AuthResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password with verification code
    - Validates code
    - Updates password
    - Returns authentication token
    """
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate new password strength
    is_valid, message = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Verify code
    verification_service = VerificationService()
    is_valid, message = verification_service.verify_code(
        db, request.email, request.code, VerificationCodeType.PASSWORD_RESET
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Update password
    user.password_hash = hash_password(request.new_password)
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Generate token (auto-login after password reset)
    token = create_access_token({"user_id": user.id})
    
    return {
        "token": token,
        "user": UserResponse.from_orm(user)
    }

@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password (requires authentication)
    - Validates old password
    - Updates to new password
    """
    # Verify old password
    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    is_valid, message = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Check if new password is same as old
    if verify_password(request.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current password"
        )
    
    # Update password
    current_user.password_hash = hash_password(request.new_password)
    db.commit()
    
    return {"message": "密码修改成功"}

# Email management endpoints
@router.post("/request-email-change")
def request_email_change(
    request: RequestEmailChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request to change email address
    - Sends verification code to new email
    """
    # Check if new email is same as current
    if request.new_email == current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New email is the same as current email"
        )
    
    # Check if new email already exists
    existing_user = db.query(User).filter(User.email == request.new_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already in use"
        )
    
    # Send verification code to new email
    verification_service = VerificationService()
    success, msg = verification_service.send_verification_email(
        db, request.new_email, VerificationCodeType.EMAIL_CHANGE
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=msg
        )
    
    return {"message": "验证码已发送到新邮箱"}

@router.post("/verify-email-change", response_model=UserResponse)
def verify_email_change(
    request: VerifyEmailChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify and complete email change
    - Validates code
    - Updates email address
    """
    # Verify code
    verification_service = VerificationService()
    is_valid, message = verification_service.verify_code(
        db, request.new_email, request.code, VerificationCodeType.EMAIL_CHANGE
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Check again if new email is available
    existing_user = db.query(User).filter(User.email == request.new_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already in use"
        )
    
    # Update email
    current_user.email = request.new_email
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)

# User info endpoints
@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserResponse.from_orm(current_user)

@router.put("/profile", response_model=UserResponse)
def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile (name, etc.)
    """
    if request.name is not None:
        current_user.name = request.name
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)

