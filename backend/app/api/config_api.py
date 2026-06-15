from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.config import ConfigUpdate, ConfigInfo
from ..models.config import SystemConfig
from ..models.user import User
from ..services.auth_service import get_current_user
from ..utils.response import success, error

router = APIRouter(prefix="/api/config", tags=["系统配置"])


@router.get("/list")
def list_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    configs = db.query(SystemConfig).all()
    return success([ConfigInfo.model_validate(c).model_dump() for c in configs])


@router.put("/update/{config_key}")
def update_config(
    config_key: str,
    req: ConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        return error("仅管理员可修改配置", 403)
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        config = SystemConfig(config_key=config_key, config_value=req.config_value)
        db.add(config)
    else:
        config.config_value = req.config_value
    db.commit()
    return success(msg="配置已更新")


@router.get("/get/{config_key}")
def get_config(
    config_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        return success({"config_key": config_key, "config_value": ""})
    return success(ConfigInfo.model_validate(config).model_dump())
