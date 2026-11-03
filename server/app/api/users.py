import uuid, pathlib
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_admin
from app.core.exceptions import BusinessError
from app.core.response import ok
from app.db.database import get_db
from app.db.models import User
from app.schemas.user import ProfileUpdate, PasswordUpdate, UserOut, AdminUserCreate, AdminUserUpdate
from app.services import user_service, auth_service  
from app.core.security import hash_password              
from app.schemas.auth import RegisterRequest  

router = APIRouter()
AVATAR_DIR = pathlib.Path("uploads/avatars")          # 相对 uvicorn 启动目录 server/
AVATAR_DIR.mkdir(parents=True, exist_ok=True)         # 目录不存在就创建
ALLOWED = {".jpg", ".jpeg", ".png", ".webp"}          # 扩展名白名单

@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),                     # File(...) = 必填的 multipart 文件字段
    user: User = Depends(get_current_user),           # 身份来自 token：上传者必须是登录用户
    db: Session = Depends(get_db),
):
    # 校验 1：扩展名白名单——放在读内容之前，便宜的错误先拒绝
    ext = pathlib.Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise BusinessError(2001, "不支持的图片格式")
    data = await file.read()                          # 一次性读入内存（头像小，可接受）
    # 校验 2：大小上限 2MB——上传接口是天然 DoS 入口，必须设限
    if len(data) > 2 * 1024 * 1024:
        raise BusinessError(2002, "图片不能超过 2MB")
    # 重命名：uuid 防路径穿越/防覆盖/防中文乱码；扩展名来自白名单，可放心拼接
    dest = AVATAR_DIR / f"{uuid.uuid4().hex}{ext}"
    dest.write_bytes(data)
    # 可访问 URL 写进用户资料并落库（/static 由 main.py 的 mount 指向 uploads/）
    user.avatar = f"/static/avatars/{dest.name}"
    db.commit()
    return ok({"avatar": user.avatar})

@router.put("/me")
def update_profile(data: ProfileUpdate,
                   user: User = Depends(get_current_user),   # me = token 里的人，前端传什么都无效
                   db: Session = Depends(get_db)):
    user_service.update_profile(db, user, data)
    db.commit()
    return ok({"nickname": user.nickname, "avatar": user.avatar})

@router.put("/me/password")                               
def update_password(data: PasswordUpdate,
                    user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    user_service.change_password(db, user, data.old_password, data.new_password)
    return ok(None)

@router.put("/{user_id}/reset-password", dependencies=[Depends(require_admin)])
def reset_password(user_id: int, db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise BusinessError(1102, "用户不存在")
    target.password_hash = hash_password("123456")   # 重置为初始密码，用户登录后自行修改
    db.commit()
    return ok()

@router.get("", dependencies=[Depends(require_admin)])
def list_users_api(page: int = 1, page_size: int = 10, keyword: str = "",
                   db: Session = Depends(get_db)):
    items, total = user_service.list_users(db, page, page_size, keyword)
    return ok({"list": [UserOut.model_validate(u) for u in items], "total": total})   # 出口海关：绝不漏 password_hash

@router.post("", dependencies=[Depends(require_admin)])
def create_user_api(data: AdminUserCreate, db: Session = Depends(get_db)):
    user = auth_service.register(db, RegisterRequest(      # 复用注册 service：查重+哈希不写第二遍
        username=data.username, nickname=data.nickname, password="123456"))
    user.role = data.role                                  # register 默认造 employee，按弹窗选择修正
    db.commit()
    return ok({"id": user.id, "username": user.username,
               "nickname": user.nickname, "role": user.role})

@router.put("/{user_id}", dependencies=[Depends(require_admin)])
def update_user_api(user_id: int, data: AdminUserUpdate, db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise BusinessError(1102, "用户不存在")
    target.nickname, target.role = data.nickname, data.role
    db.commit()
    return ok({"id": target.id, "username": target.username,
               "nickname": target.nickname, "role": target.role})

@router.delete("/{user_id}")
def delete_user_api(user_id: int, db: Session = Depends(get_db),
                    admin: User = Depends(require_admin)):
    user_service.delete_user(db, user_id, admin)           # admin 传给 service 做"不能删自己"防线
    return ok()