from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date, datetime

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    position: str
    department: str
    salary: float
    start_date: date
    status: Optional[str] = "active"
    avatar_color: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("salary")
    @classmethod
    def sal_ok(cls, v):
        if v < 0: raise ValueError("Negatif olamaz")
        return v

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = None
    start_date: Optional[date] = None
    status: Optional[str] = None
    avatar_color: Optional[str] = None
    notes: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
