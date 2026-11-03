from sqlalchemy.orm import Session
from app.core.security import verify_password, hash_password
from app.core.exceptions import BusinessError
from app.db.models import User
from app.schemas.auth import RegisterRequest

def authenticate(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not (user and verify_password(password, user.password_hash)):
        raise BusinessError(1040, "用户名或密码错误")
    return user

def register(db: Session, data: RegisterRequest) -> User:
    if db.query(User).filter(User.username == data.username).first():
        raise BusinessError(1001, "用户名已存在")
    user = User(username=data.username,
                password_hash=hash_password(data.password),
                nickname=data.nickname)
    db.add(user); db.commit(); db.refresh(user)
    return user