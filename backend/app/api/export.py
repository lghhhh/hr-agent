import io
import csv
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.candidate import Candidate
from ..models.interview import InterviewRound
from ..models.position import Position
from ..models.user import User
from ..services.auth_service import get_current_user
from ..utils.response import error

router = APIRouter(prefix="/api/export", tags=["数据导出"])


@router.get("/candidate-list")
def export_candidates(
    status: str = "",
    position_id: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Candidate)
    if status:
        q = q.filter(Candidate.current_status == status)
    if position_id:
        q = q.filter(Candidate.position_id == position_id)
    candidates = q.order_by(Candidate.id.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["姓名", "联系方式", "邮箱", "应聘岗位", "工作年限", "期望薪资", "当前状态", "创建时间"])
    status_map = {
        "pending": "待初面", "pass1": "初面通过", "pass2": "复面通过",
        "fail": "已淘汰", "offer": "拟录用",
    }
    for c in candidates:
        pos_name = ""
        if c.position_id:
            pos = db.query(Position).filter(Position.id == c.position_id).first()
            pos_name = pos.position_name if pos else ""
        writer.writerow([
            c.name, c.phone, c.email, pos_name, c.work_years,
            c.expected_salary, status_map.get(c.current_status, c.current_status),
            c.create_time.strftime("%Y-%m-%d %H:%M") if c.create_time else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=candidate_list.csv"},
    )


@router.get("/interview-report/{candidate_id}")
def export_report(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand:
        return error("候选人不存在")

    interviews = (
        db.query(InterviewRound)
        .filter(InterviewRound.candidate_id == candidate_id)
        .order_by(InterviewRound.round_num)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["=== 面试报告 ==="])
    writer.writerow(["候选人", cand.name])
    writer.writerow(["状态", cand.current_status])
    writer.writerow([""])

    for iv in interviews:
        writer.writerow([f"--- {iv.round_name} ---"])
        writer.writerow(["面试官", iv.interviewer_id])
        writer.writerow(["是否通过", "是" if iv.is_pass == 1 else "否" if iv.is_pass == 0 else "待评价"])
        if iv.fail_reason:
            writer.writerow(["淘汰原因", iv.fail_reason])
        writer.writerow(["面试官评价", iv.interviewer_comment])
        writer.writerow(["AI总结", iv.ai_summary[:500] if iv.ai_summary else ""])
        writer.writerow([""])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename=report_{cand.name}.csv"},
    )
