from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MonitoringJobCreate(BaseModel):
    x_username: str
    frequency: str  # "hourly", "daily", "every_6_hours", "every_12_hours"
    topics: Optional[List[str]] = []

class MonitoringJobUpdate(BaseModel):
    frequency: Optional[str] = None
    topics: Optional[List[str]] = None
    is_active: Optional[bool] = None

class MonitoringJobResponse(BaseModel):
    id: int
    user_id: int
    x_username: str
    frequency: str
    topics: List[str]
    is_active: bool
    created_at: datetime
    last_run: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SummaryResponse(BaseModel):
    id: int
    job_id: int
    content: str
    raw_data: dict
    created_at: datetime
    
    class Config:
        from_attributes = True

