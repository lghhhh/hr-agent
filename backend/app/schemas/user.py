from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    real_name: str
    role: str
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str
    real_name: str
    role: str = "interviewer"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    real_name: Optional[str] = None
    role: Optional[str] = None


class LoginResponse(BaseModel):
    token: str
    user: UserInfo
