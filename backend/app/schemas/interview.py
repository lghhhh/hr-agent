from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InterviewCreate(BaseModel):
    candidate_id: int
    round_num: int
    round_name: str
    interviewer_id: Optional[int] = None
    interview_time: Optional[str] = None


class InterviewUpdateSummary(BaseModel):
    interview_id: int
    ai_summary: str
    ai_summary_text: str = ""


class InterviewSubmit(BaseModel):
    interview_id: int
    interviewer_comment: str
    is_pass: int  # 1通过 0不通过 2待定
    fail_reason: str = ""
    dialogue_raw: str = ""


class InterviewInfo(BaseModel):
    id: int
    candidate_id: int
    round_num: int
    round_name: str
    interviewer_id: Optional[int] = None
    interviewer_name: Optional[str] = None
    interview_time: Optional[datetime] = None
    dialogue_raw: str
    ai_summary: str
    ai_summary_text: str = ""
    interviewer_comment: str
    is_pass: Optional[int] = None
    fail_reason: str
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIGenerateSummaryRequest(BaseModel):
    dialogue_text: str
    position_id: Optional[int] = None
    candidate_name: str = ""
