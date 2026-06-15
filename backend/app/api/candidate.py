from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..schemas.candidate import CandidateCreate, CandidateUpdate, CandidateInfo, CandidateListResp
from ..models.candidate import Candidate
from ..models.position import Position
from ..models.interview import InterviewRound
from ..models.user import User
from ..services.auth_service import get_current_user
from ..utils.response import success, error

router = APIRouter(prefix="/api/candidate", tags=["候选人管理"])


def _candidate_to_info(c: Candidate, db: Session) -> CandidateInfo:
    info = CandidateInfo.model_validate(c)
    if c.position_id:
        pos = db.query(Position).filter(Position.id == c.position_id).first()
        if pos:
            info.position_name = pos.position_name
    return info


@router.get("/list")
def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query("", alias="status"),
    position_id: int = Query(0, alias="position_id"),
    keyword: str = Query("", alias="keyword"),
    db: Session = Depends(get_db),
):
    q = db.query(Candidate)
    if status:
        q = q.filter(Candidate.current_status == status)
    if position_id:
        q = q.filter(Candidate.position_id == position_id)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            Candidate.name.like(like) | Candidate.phone.like(like) | Candidate.email.like(like)
        )
    total = q.count()
    items = q.order_by(desc(Candidate.update_time)).offset((page - 1) * page_size).limit(page_size).all()
    return success(
        CandidateListResp(
            total=total,
            items=[_candidate_to_info(c, db).model_dump() for c in items],
        ).model_dump()
    )


@router.post("/add")
def add_candidate(
    req: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cand = Candidate(
        name=req.name,
        phone=req.phone,
        email=req.email,
        position_id=req.position_id,
        work_years=req.work_years,
        expected_salary=req.expected_salary,
        resume_url=req.resume_url,
        current_status="pending",
        current_round=0,
    )
    db.add(cand)
    db.commit()
    db.refresh(cand)
    return success(_candidate_to_info(cand, db).model_dump(), "添加成功")


@router.put("/update")
def update_candidate(
    cand_id: int,
    req: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cand = db.query(Candidate).filter(Candidate.id == cand_id).first()
    if not cand:
        return error("候选人不存在")
    update_data = req.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(cand, key, val)
    db.commit()
    db.refresh(cand)
    return success(_candidate_to_info(cand, db).model_dump(), "更新成功")


@router.delete("/delete")
def delete_candidate(
    cand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cand = db.query(Candidate).filter(Candidate.id == cand_id).first()
    if not cand:
        return error("候选人不存在")
    # Delete all interview records
    db.query(InterviewRound).filter(InterviewRound.candidate_id == cand_id).delete()
    db.delete(cand)
    db.commit()
    return success(msg="删除成功")


@router.get("/detail/{cand_id}")
def candidate_detail(
    cand_id: int,
    db: Session = Depends(get_db),
):
    cand = db.query(Candidate).filter(Candidate.id == cand_id).first()
    if not cand:
        return error("候选人不存在")
    info = _candidate_to_info(cand, db)
    interviews = (
        db.query(InterviewRound)
        .filter(InterviewRound.candidate_id == cand_id)
        .order_by(InterviewRound.round_num)
        .all()
    )
    interview_list = []
    for iv in interviews:
        d = {
            "id": iv.id,
            "round_num": iv.round_num,
            "round_name": iv.round_name,
            "interviewer_id": iv.interviewer_id,
            "interview_time": iv.interview_time.isoformat() if iv.interview_time else None,
            "dialogue_raw": iv.dialogue_raw,
            "ai_summary": iv.ai_summary,
            "ai_summary_text": iv.ai_summary_text,
            "interviewer_comment": iv.interviewer_comment,
            "is_pass": iv.is_pass,
            "fail_reason": iv.fail_reason,
            "create_time": iv.create_time.isoformat() if iv.create_time else None,
        }
        if iv.interviewer_id:
            u = db.query(User).filter(User.id == iv.interviewer_id).first()
            d["interviewer_name"] = u.real_name if u else None
        interview_list.append(d)

    return success({
        "candidate": info.model_dump(),
        "interviews": interview_list,
    })
