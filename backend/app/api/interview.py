from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..schemas.interview import InterviewCreate, InterviewUpdateSummary, InterviewSubmit
from ..models.interview import InterviewRound
from ..models.candidate import Candidate
from ..models.user import User
from ..services.auth_service import get_current_user
from ..utils.response import success, error

router = APIRouter(prefix="/api/interview", tags=["面试流程"])


@router.post("/create")
def create_interview(
    req: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cand = db.query(Candidate).filter(Candidate.id == req.candidate_id).first()
    if not cand:
        return error("候选人不存在")

    iv = InterviewRound(
        candidate_id=req.candidate_id,
        round_num=req.round_num,
        round_name=req.round_name,
        interviewer_id=req.interviewer_id or current_user.id,
        interview_time=datetime.fromisoformat(req.interview_time) if req.interview_time else None,
    )
    db.add(iv)
    db.commit()
    db.refresh(iv)
    return success({
        "id": iv.id,
        "round_num": iv.round_num,
        "round_name": iv.round_name,
    }, "面试记录创建成功")


@router.put("/update-summary")
def update_summary(
    req: InterviewUpdateSummary,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    iv = db.query(InterviewRound).filter(InterviewRound.id == req.interview_id).first()
    if not iv:
        return error("面试记录不存在")
    iv.ai_summary = req.ai_summary
    iv.ai_summary_text = req.ai_summary_text
    db.commit()
    return success(msg="AI总结已更新")


@router.post("/submit")
def submit_interview(
    req: InterviewSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    iv = db.query(InterviewRound).filter(InterviewRound.id == req.interview_id).first()
    if not iv:
        return error("面试记录不存在")

    iv.interviewer_comment = req.interviewer_comment
    iv.is_pass = req.is_pass
    iv.fail_reason = req.fail_reason
    if req.dialogue_raw:
        iv.dialogue_raw = req.dialogue_raw

    cand = db.query(Candidate).filter(Candidate.id == iv.candidate_id).first()
    if not cand:
        return error("候选人不存在")

    if req.is_pass == 1:
        # 通过：流转到下一轮
        total_rounds = 3  # 默认3轮，可配置
        if iv.round_num >= total_rounds:
            cand.current_status = "offer"  # 终面通过 → 拟录用
        else:
            cand.current_status = f"pass{iv.round_num}"  # pass1/pass2
        cand.current_round = iv.round_num
    elif req.is_pass == 0:
        # 不通过
        cand.current_status = "fail"
    elif req.is_pass == 2:
        # 待定：标记为审核中，不流转不淘汰
        cand.current_status = "pending_review"
        cand.current_round = iv.round_num

    db.commit()
    db.refresh(iv)
    return success({
        "interview_id": iv.id,
        "candidate_status": cand.current_status,
    }, "面试结果已提交")


@router.get("/detail/{interview_id}")
def interview_detail(
    interview_id: int,
    db: Session = Depends(get_db),
):
    iv = db.query(InterviewRound).filter(InterviewRound.id == interview_id).first()
    if not iv:
        return error("面试记录不存在")
    d = {
        "id": iv.id,
        "candidate_id": iv.candidate_id,
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
    return success(d)
