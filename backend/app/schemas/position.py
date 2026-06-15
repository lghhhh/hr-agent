from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PositionCreate(BaseModel):
    position_name: str
    department: str = ""
    description: str = ""


class PositionUpdate(BaseModel):
    position_name: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None


class PositionInfo(BaseModel):
    id: int
    position_name: str
    department: str
    description: str
    status: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class PositionListResp(BaseModel):
    total: int
    items: list[PositionInfo]
