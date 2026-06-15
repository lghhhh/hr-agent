from sqlalchemy import Column, Integer, String, Text, SmallInteger, DateTime
from sqlalchemy.sql import func
from ..database import Base


class Position(Base):
    __tablename__ = "recruit_position"

    id = Column(Integer, primary_key=True, autoincrement=True)
    position_name = Column(String(128), nullable=False)
    department = Column(String(128), default="")
    description = Column(Text, default="")
    status = Column(SmallInteger, default=1)  # 1开启 0关闭
    create_time = Column(DateTime, server_default=func.now())
