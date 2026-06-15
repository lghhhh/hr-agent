from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..database import Base


class SystemConfig(Base):
    __tablename__ = "sys_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(128), unique=True, nullable=False, index=True)
    config_value = Column(Text, default="")
    description = Column(String(256), default="")
