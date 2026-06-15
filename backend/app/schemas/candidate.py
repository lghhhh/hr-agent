from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CandidateCreate(BaseModel):
    name: str
    phone: str = ""
    email: str = ""
    position_id: Optional[int] = None
    work_years: str = ""
    expected_salary: str = ""
    resume_url: str = ""


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    position_id: Optional[int] = None
    work_years: Optional[str] = None
    expected_salary: Optional[str] = None
    resume_url: Optional[str] = None


class CandidateInfo(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    position_id: Optional[int] = None
    position_name: Optional[str] = None
    work_years: str
    expected_salary: str
    resume_url: str
    current_status: str
    current_round: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class CandidateListResp(BaseModel):
    total: int
    items: list[CandidateInfo]


class InterviewSummary(BaseModel):
    candidate_name: str
    position: str
    work_years: str
    expected_salary: str
    skill_match: str
    project_highlights: str
    qa_summary: str
    strengths: str
    weaknesses: str
    overall_assessment: str
