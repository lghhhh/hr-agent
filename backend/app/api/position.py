from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.position import PositionCreate, PositionUpdate, PositionInfo
from ..models.position import Position
from ..models.user import User
from ..services.auth_service import get_current_user
from ..utils.response import success, error

router = APIRouter(prefix="/api/position", tags=["岗位管理"])


@router.get("/list")
def list_positions(db: Session = Depends(get_db)):
    positions = db.query(Position).order_by(Position.id.desc()).all()
    return success([PositionInfo.model_validate(p).model_dump() for p in positions])


@router.post("/add")
def add_position(
    req: PositionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pos = Position(**req.model_dump())
    db.add(pos)
    db.commit()
    db.refresh(pos)
    return success(PositionInfo.model_validate(pos).model_dump(), "创建成功")


@router.put("/update")
def update_position(
    req: PositionUpdate,
    pos_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pos = db.query(Position).filter(Position.id == pos_id).first()
    if not pos:
        return error("岗位不存在")
    update_data = req.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(pos, key, val)
    db.commit()
    db.refresh(pos)
    return success(PositionInfo.model_validate(pos).model_dump(), "更新成功")


@router.delete("/delete")
def delete_position(
    pos_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pos = db.query(Position).filter(Position.id == pos_id).first()
    if not pos:
        return error("岗位不存在")
    db.delete(pos)
    db.commit()
    return success(msg="删除成功")
