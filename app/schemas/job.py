from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from uuid import UUID

class JobCreate(BaseModel):
    company_name: str
    position: str
    status: str = 'applied'
    applied_on: date

class JobUpdate(BaseModel):
    company_name: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    applied_on: Optional[date] = None

class JobResponse(BaseModel):
    id: UUID
    user_id: UUID
    company_name: str
    position: str
    status: str
    applied_on: date
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 