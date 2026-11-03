from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_admin
from app.core.exceptions import BusinessError
from app.core.response import ok
from app.db.database import get_db
from app.db.models import Lab, Reservation, User
from app.services import reservation_service

router = APIRouter()

class ReservationCreate(BaseModel):
    lab_id: int
    date: str          # "YYYY-MM-DD"
    start_time: str    # "HH:MM"
    end_time: str      # "HH:MM"
    purpose: str

class ReviewAction(BaseModel):
    action: str        # "approved" | "rejected"
    comment: str = ""

def _brief(r: Reservation, lab_name: str = "") -> dict:
    """统一序列化：列表/详情共用一个形状，前端只写一种渲染"""
    return {"id": r.id, "lab_name": lab_name, "date": str(r.date),
            "start_time": str(r.start_time), "end_time": str(r.end_time),
            "purpose": r.purpose, "status": r.status, "review_comment": r.review_comment}

@router.post("")
def create(data: ReservationCreate, user: User = Depends(get_current_user),
           db: Session = Depends(get_db)):
    # user_id 一律取 token 的 user——不信请求体（越权防线）
    resv = reservation_service.create(db, user.id, data.lab_id,
                                      data.date, data.start_time, data.end_time, data.purpose)
    return ok({"id": resv.id, "status": resv.status})

@router.get("/mine")
def mine(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(Reservation).filter(Reservation.user_id == user.id)
              .order_by(Reservation.id.desc()).all())
    # 一次查全部实验室名建映射，避免循环里逐条查库（N+1 问题）
    labs = {l.id: l.name for l in db.query(Lab)}
    return ok([_brief(r, labs.get(r.lab_id, "")) for r in rows])

@router.put("/{resv_id}/cancel")
def cancel(resv_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resv = db.get(Reservation, resv_id)
    # 双保险 1：只能取消自己的（水平越权防线）
    if not resv or resv.user_id != user.id:
        raise BusinessError(3002, "预约不存在或无权操作")
    # 双保险 2：状态流转合法性由 transition 把关（非法流转直接 3001）
    reservation_service.transition(resv, "cancelled")
    db.commit()
    return ok()

@router.get("/pending")
def pending(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    rows = (db.query(Reservation).filter(Reservation.status == "pending")
              .order_by(Reservation.id.desc()).all())
    labs = {l.id: l.name for l in db.query(Lab)}
    return ok([_brief(r, labs.get(r.lab_id, "")) for r in rows])

@router.put("/{resv_id}/review")
def review(resv_id: int, data: ReviewAction,
           user: User = Depends(require_admin), db: Session = Depends(get_db)):
    resv = db.get(Reservation, resv_id)
    if not resv:
        raise BusinessError(3002, "预约不存在")
    if data.action not in ("approved", "rejected"):
        raise BusinessError(3003, "非法的审核动作")
    reservation_service.transition(resv, data.action, comment=data.comment)
    db.commit()
    return ok()