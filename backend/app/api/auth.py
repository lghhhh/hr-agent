from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.user import LoginRequest, UserInfo, LoginResponse, UserCreate, UserUpdate
from ..services.auth_service import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
)
from ..models.user import User
from ..utils.response import success, error, unauthorized

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, req.username, req.password)
    if not user:
        return unauthorized("账号或密码错误")
    token = create_access_token({"user_id": user.id, "role": user.role})
    return success(
        LoginResponse(
            token=token,
            user=UserInfo.model_validate(user),
        ).model_dump()
    )


@router.get("/userinfo")
def get_userinfo(current_user: User = Depends(get_current_user)):
    return success(UserInfo.model_validate(current_user).model_dump())


@router.get("/users")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        return error("仅管理员可查看用户列表", 403)
    users = db.query(User).all()
    return success([UserInfo.model_validate(u).model_dump() for u in users])


@router.post("/users")
def create_user(
    req: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        return error("仅管理员可创建用户", 403)
    exist = db.query(User).filter(User.username == req.username).first()
    if exist:
        return error("用户名已存在")
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        real_name=req.real_name,
        role=req.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return success(UserInfo.model_validate(user).model_dump(), "创建成功")
