import jwt as pyjwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.db.database import get_db
from app.db.models import User

bearer = HTTPBearer(auto_error=False)

def get_current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if cred is None:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = decode_token(cred.credentials)
    except pyjwt.PyJWTError:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user