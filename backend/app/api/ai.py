from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

from ..database import get_db
from ..schemas.interview import AIGenerateSummaryRequest
from ..models.position import Position
from ..models.user import User
from ..services.ai_service import generate_summary
from ..services.auth_service import get_current_user
from ..utils.response import success, error

router = APIRouter(prefix="/api/ai", tags=["AI解析"])


@router.post("/generate-summary")
async def generate_summary_api(
    req: AIGenerateSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not req.dialogue_text or len(req.dialogue_text.strip()) < 10:
        return error("面试对话文本太短，请至少输入10个字符")

    position_name = ""
    if req.position_id:
        pos = db.query(Position).filter(Position.id == req.position_id).first()
        if pos:
            position_name = pos.position_name

    result = await generate_summary(
        dialogue_text=req.dialogue_text,
        candidate_name=req.candidate_name,
        position_name=position_name,
    )

    if result is None:
        return error("AI解析失败，请检查大模型API配置")

    return success(result)
