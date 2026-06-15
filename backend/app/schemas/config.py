from pydantic import BaseModel
from typing import Optional


class ConfigUpdate(BaseModel):
    config_value: str


class ConfigInfo(BaseModel):
    id: int
    config_key: str
    config_value: str
    description: str

    class Config:
        from_attributes = True
