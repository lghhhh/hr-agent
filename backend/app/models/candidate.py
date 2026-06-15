from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class Candidate(Base):
    __tablename__ = "candidate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    phone = Column(String(32), default="")
    email = Column(String(128), default="")
    position_id = Column(Integer, ForeignKey("recruit_position.id"), nullable=True)
    work_years = Column(String(32), default="")
    expected_salary = Column(String(64), default="")
    resume_url = Column(String(512), default="")
    current_status = Column(String(32), default="pending")
    # pending / pass1 / pass2 / fail / offer
    current_round = Column(Integer, default=0)
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
