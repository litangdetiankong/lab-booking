from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import create_token
from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services import auth_service

router = APIRouter()

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, data.username, data.password)  # 失败在 service 里 raise
    token = create_token(user.id, user.role)                            # 真 JWT（3.2）
    return {"code": 0, "message": "ok", "data": {"token": token, "nickname": user.nickname, "role": user.role}}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    """试金石接口：能带着合法 token 到这里，整条认证链路就通了"""
    return {"code": 0, "message": "ok",
            "data": {"id": user.id, "username": user.username,
                     "nickname": user.nickname, "avatar": user.avatar, "role": user.role}}

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register(db, data)
    return {"code": 0, "message": "ok",
            "data": {"id": user.id, "username": user.username, "nickname": user.nickname}}