from sqlalchemy.orm import Session
from app.core.exceptions import BusinessError
from app.core.security import verify_password, hash_password
from app.db.models import Reservation, User

def update_profile(db: Session, user: User, data) -> None:
    # 逐字段判断 None：PUT 的语义是"只改传了的字段"。
    # 若整体覆盖，前端只想改昵称时，没传的字段会被 None 意外清空
    if data.nickname is not None:
        user.nickname = data.nickname

def change_password(db: Session, user: User, old: str, new: str) -> None:
    # 第 1 步：验证旧密码——防止"捡到别人开着的电脑"直接改密码
    if not verify_password(old, user.password_hash):
        raise BusinessError(2101, "旧密码不正确")
    # 第 2 步：新密码哈希后覆盖。注意：已签发的 JWT 仍然有效（JWT 无状态），
    # 所以前端在成功回调里清 token 踢回登录页，双保险
    user.password_hash = hash_password(new)
    db.commit()
    # 第 3 步（前端侧）：改密成功 → localStorage.removeItem('token') → 跳 /login

def list_users(db, page: int = 1, page_size: int = 10, keyword: str = ""):
    q = db.query(User)
    if keyword:
        q = q.filter(User.username.contains(keyword) | User.nickname.contains(keyword))
    total = q.count()
    items = q.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total

def delete_user(db: Session, user_id: int, current: User) -> None:
    # 防线 1：不能删自己——防手滑把自己锁在系统外
    if user_id == current.id:
        raise BusinessError(1101, "不能删除自己")
    target = db.get(User, user_id)
    if not target:
        raise BusinessError(1102, "用户不存在")
    # 防线 2：不能删管理员——管理员是系统的最后防线，删光就失控了
    if target.role == "admin":
        raise BusinessError(1103, "不能删除管理员账号")
    if db.query(Reservation).filter(Reservation.user_id == user_id).count():
        raise BusinessError(1104, "该用户存在预约记录，无法删除")
    db.delete(target)
    db.commit()