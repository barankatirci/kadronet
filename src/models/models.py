from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text
from sqlalchemy.sql import func
from src.data.database import Base

class Employee(Base):
    __tablename__ = "employees"
    id           = Column(Integer, primary_key=True, index=True)
    first_name   = Column(String(100), nullable=False)
    last_name    = Column(String(100), nullable=False)
    email        = Column(String(200), unique=True, nullable=False, index=True)
    phone        = Column(String(30))
    position     = Column(String(150), nullable=False)
    department   = Column(String(100), nullable=False)
    salary       = Column(Float, nullable=False, default=0.0)
    start_date   = Column(Date, nullable=False)
    status       = Column(String(20), nullable=False, default="active")
    avatar_color = Column(String(7))
    notes        = Column(Text)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String(100), unique=True, nullable=False, index=True)
    password   = Column(String(200), nullable=False)
    full_name  = Column(String(200))
    role       = Column(String(20), default="admin")
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
