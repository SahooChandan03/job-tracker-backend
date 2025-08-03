from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class NoteCreate(BaseModel):
    job_id: UUID
    content: str
    reminder_time: Optional[datetime] = None

class NoteResponse(BaseModel):
    id: UUID
    user_id: UUID
    job_id: UUID
    content: str
    reminder_time: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True 