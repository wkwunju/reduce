from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, ARRAY, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

try:
    from app.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

class UserStatus(str, enum.Enum):
    """User account status"""
    UNVERIFIED = "unverified"  # Email not verified yet
    ACTIVE = "active"          # Normal active user
    SUSPENDED = "suspended"    # Account suspended/banned

class JobStatus(str, enum.Enum):
    """Job lifecycle status"""
    ACTIVE = "active"
    DELETED = "deleted"

class VerificationCodeType(str, enum.Enum):
    """Type of verification code"""
    EMAIL_VERIFICATION = "email_verification"  # For email activation
    PASSWORD_RESET = "password_reset"          # For password reset
    EMAIL_CHANGE = "email_change"              # For changing email

class ExecutionStatus(str, enum.Enum):
    """Job execution status"""
    RUNNING = "running"      # Currently executing
    COMPLETED = "completed"  # Successfully completed
    FAILED = "failed"        # Failed with error

class NotificationChannel(str, enum.Enum):
    """Notification delivery channel"""
    TELEGRAM = "telegram"
    EMAIL = "email"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)  # Optional display name
    status = Column(Enum(UserStatus), default=UserStatus.UNVERIFIED, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    notification_targets = relationship("NotificationTarget", back_populates="user", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    x_username = Column(String(255), nullable=False, index=True)
    frequency = Column(String(50), nullable=False)
    topics = Column(JSON, default=list)  # Store as JSON for SQLite/PostgreSQL compatibility
    language = Column(String(20), nullable=False, default="en")
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.ACTIVE, nullable=False, index=True)
    notification_target_id = Column(Integer, ForeignKey("notification_targets.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_run = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="jobs")
    summaries = relationship("Summary", back_populates="job", cascade="all, delete-orphan")
    executions = relationship("JobExecution", back_populates="job", cascade="all, delete-orphan")
    notification_target = relationship("NotificationTarget")
    notification_targets = relationship(
        "NotificationTarget",
        secondary="job_notification_targets",
        back_populates="jobs"
    )

class JobExecution(Base):
    __tablename__ = "job_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.RUNNING, nullable=False)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    tweets_fetched = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    job = relationship("Job", back_populates="executions")
    summaries = relationship("Summary", back_populates="execution")

class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # For scheduled tasks
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True, index=True)
    execution_id = Column(Integer, ForeignKey("job_executions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # For playground runs
    is_playground = Column(Boolean, default=False, nullable=False, index=True)
    x_username = Column(String(255), nullable=True)  # For playground runs
    topics = Column(JSON, nullable=True)  # For playground runs
    hours_back = Column(Integer, nullable=True)  # For playground runs
    
    # Common fields
    content = Column(Text, nullable=False)
    tweets_count = Column(Integer, default=0)
    raw_data = Column(JSON, nullable=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    job = relationship("Job", back_populates="summaries")
    execution = relationship("JobExecution", back_populates="summaries")

class NotificationTarget(Base):
    __tablename__ = "notification_targets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(Enum(NotificationChannel), nullable=False, index=True)
    destination = Column(String(255), nullable=False)
    meta = Column(JSON, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="notification_targets")
    jobs = relationship(
        "Job",
        secondary="job_notification_targets",
        back_populates="notification_targets"
    )

class JobNotificationTarget(Base):
    __tablename__ = "job_notification_targets"

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    notification_target_id = Column(Integer, ForeignKey("notification_targets.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NotificationBindToken(Base):
    __tablename__ = "notification_bind_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(Enum(NotificationChannel), nullable=False, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    code = Column(String(6), nullable=False)  # 6-digit code
    code_type = Column(Enum(VerificationCodeType), nullable=False)
    used = Column(Boolean, default=False)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
