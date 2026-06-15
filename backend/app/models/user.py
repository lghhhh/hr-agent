from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..database import Base


class User(Base):
    __tablename__ = "sys_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    real_name = Column(String(64), nullable=False)
    role = Column(String(32), default="admin")  # admin / interviewer
    create_time = Column(DateTime, server_default=func.now())
