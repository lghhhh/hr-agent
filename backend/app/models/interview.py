from sqlalchemy import Column, Integer, String, Text, SmallInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class InterviewRound(Base):
    __tablename__ = "interview_round"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidate.id"), nullable=False, index=True)
    round_num = Column(Integer, nullable=False)
    round_name = Column(String(64), default="")
    interviewer_id = Column(Integer, ForeignKey("sys_user.id"), nullable=True)
    interview_time = Column(DateTime, nullable=True)
    dialogue_raw = Column(Text, default="")
    ai_summary = Column(Text, default="")  # JSON format
    ai_summary_text = Column(Text, default="")  # 干净的报告文字
    interviewer_comment = Column(String(1024), default="")
    is_pass = Column(SmallInteger, nullable=True)  # 1通过 0不通过 NULL待评价
    fail_reason = Column(String(512), default="")
    create_time = Column(DateTime, server_default=func.now())
