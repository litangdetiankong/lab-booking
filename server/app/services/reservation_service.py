from datetime import date, datetime
from sqlalchemy.orm import Session
from app.core.exceptions import BusinessError
from app.db.models import Lab, Reservation

TRANSITIONS = {
    "pending":   {"approved", "rejected", "cancelled"},
    "approved":  {"cancelled"},
    "rejected":  set(),
    "cancelled": set(),
}

def transition(resv: Reservation, target: str, comment: str = "") -> None:
    if target not in TRANSITIONS[resv.status]:
        raise BusinessError(3001, f"预约当前状态为 {resv.status}，不能变更为 {target}")
    resv.status = target
    if comment:
        resv.review_comment = comment

def has_conflict(db, lab_id: int, d, start, end) -> bool:
    q = db.query(Reservation).filter(
        Reservation.lab_id == lab_id,
        Reservation.date == d,
        Reservation.status.in_(["pending", "approved"]),   # 取消/驳回的不算占位
        Reservation.start_time < end,      # 旧记录开始早于新记录结束
        Reservation.end_time > start,      # 旧记录结束晚于新记录开始
    )
    return db.query(q.exists()).scalar()

def create(db, user_id: int, lab_id: int, d, start, end, purpose: str) -> Reservation:
    """三层校验全部收在这里——api 层只管调它，前端只管展示错误"""
    lab = db.get(Lab, lab_id)
    if not lab:
        raise BusinessError(3101, "实验室不存在")
    if lab.status != "开放中":
        raise BusinessError(3102, "实验室维护中，暂不开放预约")
    d = datetime.strptime(d, "%Y-%m-%d").date() if isinstance(d, str) else d
    start_t = datetime.strptime(start, "%H:%M").time() if isinstance(start, str) else start
    end_t = datetime.strptime(end, "%H:%M").time() if isinstance(end, str) else end
    if d < date.today():
        raise BusinessError(3103, "预约日期不能是过去")
    if start_t >= end_t:
        raise BusinessError(3104, "开始时间必须早于结束时间")
    if start_t < lab.open_time_start or end_t > lab.open_time_end:
        raise BusinessError(3105, f"超出开放时段（{lab.open_time_start}-{lab.open_time_end}）")
    if has_conflict(db, lab_id, d, start_t, end_t):
        raise BusinessError(3106, "该时段已被预约，请换一个时间")
    resv = Reservation(user_id=user_id, lab_id=lab_id, date=d,
                       start_time=start_t, end_time=end_t, purpose=purpose)
    db.add(resv); db.commit(); db.refresh(resv)
    return resv