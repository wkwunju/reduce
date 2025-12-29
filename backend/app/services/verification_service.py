import random
import string
from datetime import datetime, timedelta
from typing import Tuple
from sqlalchemy.orm import Session
from app.models import VerificationCode, VerificationCodeType
from app.services.sendgrid_service import SendGridService

class VerificationService:
    """Service for managing verification codes"""
    
    def __init__(self):
        self.email_service = SendGridService()
    
    def generate_code(self) -> str:
        """Generate a random 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_verification_email(
        self, 
        db: Session, 
        email: str, 
        code_type: VerificationCodeType
    ) -> Tuple[bool, str]:
        """
        Generate and send a verification code via email
        
        Args:
            db: Database session
            email: Recipient email address
            code_type: Type of verification code
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Generate verification code
            code = self.generate_code()
            
            # Set expiration time based on code type
            if code_type == VerificationCodeType.PASSWORD_RESET:
                expires_minutes = 10
            else:
                expires_minutes = 5
            
            expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
            
            # Save to database
            db_code = VerificationCode(
                email=email,
                code=code,
                code_type=code_type,
                expires_at=expires_at
            )
            db.add(db_code)
            db.commit()
            
            # Send email
            subject, html_content = self._get_email_content(code, code_type)
            # Extract plain text from HTML (simple version)
            text_content = f"Your verification code is: {code}\n\nValid for: {expires_minutes}minutes"
            self.email_service.send_email(email, subject, text_content, html_content)
            
            return True, "Verification code sent"
        except Exception as e:
            db.rollback()
            return False, f"Failed to send: {str(e)}"
    
    def verify_code(
        self, 
        db: Session, 
        email: str, 
        code: str, 
        code_type: VerificationCodeType
    ) -> Tuple[bool, str]:
        """
        Verify a verification code
        
        Args:
            db: Database session
            email: Email address
            code: Verification code to check
            code_type: Type of verification code
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        # Find matching unused code
        db_code = db.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.code_type == code_type,
            VerificationCode.used == False,
            VerificationCode.expires_at > datetime.utcnow()
        ).first()
        
        if not db_code:
            return False, "Invalid or expired verification code"
        
        # Mark as used
        db_code.used = True
        db.commit()
        
        return True, "Verification successful"
    
    def _get_email_content(
        self, 
        code: str, 
        code_type: VerificationCodeType
    ) -> Tuple[str, str]:
        """
        Get email subject and content based on code type
        
        Args:
            code: Verification code
            code_type: Type of verification code
        
        Returns:
            Tuple[str, str]: (subject, html_content)
        """
        templates = {
            VerificationCodeType.EMAIL_VERIFICATION: (
                "Verify Your XTrack Account",
                f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Welcome to XTrack!</h2>
                    <p>Your verification code is: </p>
                    <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #000;">
                        {code}
                    </div>
                    <p style="color: #666; margin-top: 20px;">此验证码5minutes内有效。</p>
                    <p style="color: #666;">If you did not sign up for XTrack, please ignore this email.</p>
                </div>
                """
            ),
            VerificationCodeType.PASSWORD_RESET: (
                "Reset Your XTrack Password",
                f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Reset Your Password</h2>
                    <p>您请求重置 XTrack 账号密码。Your verification code is: </p>
                    <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #000;">
                        {code}
                    </div>
                    <p style="color: #666; margin-top: 20px;">此验证码10minutes内有效。</p>
                    <p style="color: #666;">If you did not request a password reset, please ignore this email and ensure your account is secure.</p>
                </div>
                """
            ),
            VerificationCodeType.EMAIL_CHANGE: (
                "Change XTrack Email",
                f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Verify New Email</h2>
                    <p>您正在更换 XTrack 账号的邮箱地址。Your verification code is: </p>
                    <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #000;">
                        {code}
                    </div>
                    <p style="color: #666; margin-top: 20px;">此验证码5minutes内有效。</p>
                    <p style="color: #666;">If you did not request an email change, please login to your account and check security settings immediately.</p>
                </div>
                """
            )
        }
        
        return templates.get(code_type, ("XTrack Verification Code", f"Your verification code is: {code}"))

