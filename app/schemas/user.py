from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 


class VerifyOTP(BaseModel):
    email: EmailStr
    code: str
    module: str = "register"  # "register", "login", or "forgetpassword"

class ResendOTP(BaseModel):
    email: EmailStr
    module: str = "register"  # "register", "login", or "forgetpassword"

class ForgetPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str