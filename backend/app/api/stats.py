from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from ..database import get_db
from ..models.candidate import Candidate
from ..models.interview import InterviewRound
from ..models.position import Position
from ..models.user import User
from ..services.auth_service import get_current_user
from ..utils.response import success

router = APIRouter(prefix="/api/stats", tags=["统计看板"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    total_candidates = db.query(func.count(Candidate.id)).scalar() or 0
    pending = db.query(func.count(Candidate.id)).filter(Candidate.current_status == "pending").scalar() or 0
    fail = db.query(func.count(Candidate.id)).filter(Candidate.current_status == "fail").scalar() or 0
    offer = db.query(func.count(Candidate.id)).filter(Candidate.current_status == "offer").scalar() or 0
    pass1 = db.query(func.count(Candidate.id)).filter(Candidate.current_status == "pass1").scalar() or 0
    pass2 = db.query(func.count(Candidate.id)).filter(Candidate.current_status == "pass2").scalar() or 0
    total_interviews = db.query(func.count(InterviewRound.id)).scalar() or 0
    total_positions = db.query(func.count(Position.id)).filter(Position.status == 1).scalar() or 0

    pass_count = pass1 + pass2 + offer
    pass_rate = round((pass_count / total_candidates * 100), 1) if total_candidates > 0 else 0

    return success({
        "total_candidates": total_candidates,
        "pending_interview": pending,
        "eliminated": fail,
        "offered": offer,
        "pass1": pass1,
        "pass2": pass2,
        "total_interviews": total_interviews,
        "total_positions": total_positions,
        "pass_rate": pass_rate,
    })


@router.get("/trend")
def trend(days: int = 30, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    start_date = datetime.utcnow() - timedelta(days=days)

    # Daily new candidates
    daily_new = (
        db.query(
            func.date(Candidate.create_time).label("date"),
            func.count(Candidate.id).label("count"),
        )
        .filter(Candidate.create_time >= start_date)
        .group_by(func.date(Candidate.create_time))
        .order_by(func.date(Candidate.create_time))
        .all()
    )

    # Daily interviews completed
    daily_interviews = (
        db.query(
            func.date(InterviewRound.create_time).label("date"),
            func.count(InterviewRound.id).label("count"),
        )
        .filter(InterviewRound.create_time >= start_date)
        .group_by(func.date(InterviewRound.create_time))
        .order_by(func.date(InterviewRound.create_time))
        .all()
    )

    return success({
        "daily_new": [{"date": str(r.date), "count": r.count} for r in daily_new],
        "daily_interviews": [{"date": str(r.date), "count": r.count} for r in daily_interviews],
    })


@router.get("/position")
def position_stats(db: Session = Depends(get_db)):
    positions = db.query(Position).filter(Position.status == 1).all()
    result = []
    for pos in positions:
        total = db.query(func.count(Candidate.id)).filter(Candidate.position_id == pos.id).scalar() or 0
        interviewed = (
            db.query(func.count(Candidate.id))
            .filter(Candidate.position_id == pos.id, Candidate.current_round > 0)
            .scalar() or 0
        )
        passed = (
            db.query(func.count(Candidate.id))
            .filter(
                Candidate.position_id == pos.id,
                Candidate.current_status.in_(["pass1", "pass2", "offer"]),
            )
            .scalar() or 0
        )
        pass_rate = round((passed / interviewed * 100), 1) if interviewed > 0 else 0
        result.append({
            "position_name": pos.position_name,
            "department": pos.department,
            "total": total,
            "interviewed": interviewed,
            "passed": passed,
            "pass_rate": pass_rate,
        })
    return success(result)
