from sqlalchemy import or_, case
from app.core.exceptions import BusinessError
from app.db.models import Lab, Reservation

def list_labs(db, keyword: str = "", capacity_min: int = 0, status: str | None = None) -> list[Lab]:
    """实验室查询：人员端、管理端、AI 工具三处共用这一个函数。
    参数用业务语义（capacity_min 而不是 filter_json）——阶段四的模型靠参数名理解工具"""
    q = db.query(Lab)
    if keyword:            # 关键词同时模糊匹配三个字段，or_ 把条件"或"起来
        like = f"%{keyword}%"
        q = q.filter(or_(Lab.name.like(like), Lab.description.like(like), Lab.location.like(like)))
    if capacity_min:       # 容量下限：只留坐得下这么多人的
        q = q.filter(Lab.capacity >= capacity_min)
    if status:             # 管理端会传 status 精确筛选；不传就不加这个条件
        q = q.filter(Lab.status == status)
    # 维护中排最后 + 名称排序：展示规则只写这一处（步骤 8 的决策）
    return q.order_by(case((Lab.status == "维护中", 1), else_=0), Lab.name).all()

def get_lab(db, lab_id: int) -> Lab | None:
    return db.get(Lab, lab_id)          # 按主键查的标准姿势

def create_lab(db, data: dict) -> Lab:
    from datetime import datetime
    # TIME 字段：把 "09:00" 字符串转成 time 对象再入库，别赌驱动帮你转
    data = {**data,
            "open_time_start": datetime.strptime(data["open_time_start"], "%H:%M").time(),
            "open_time_end":   datetime.strptime(data["open_time_end"],   "%H:%M").time()}
    lab = Lab(**data)                   # dict 展开成模型字段
    db.add(lab); db.commit(); db.refresh(lab)
    return lab

def update_lab(db, lab_id: int, data: dict) -> Lab | None:
    lab = db.get(Lab, lab_id)
    if not lab:
        return None
    if "open_time_start" in data:       # 有时段字段才需要转换
        from datetime import datetime
        data["open_time_start"] = datetime.strptime(data["open_time_start"], "%H:%M").time()
        data["open_time_end"]   = datetime.strptime(data["open_time_end"],   "%H:%M").time()
    for k, v in data.items():           # 只更新传了的字段（同步骤 5 的逐字段思路）
        setattr(lab, k, v)
    db.commit()
    return lab

def delete_lab(db, lab_id: int) -> None:
    lab = db.get(Lab, lab_id)
    if not lab:
        raise BusinessError(4101, "实验室不存在")
    if db.query(Reservation).filter(Reservation.lab_id == lab_id).count():
        raise BusinessError(4103, "该实验室存在预约记录，无法删除")
    db.delete(lab)                  # 设备随 FK 的 CASCADE 一起删
    db.commit()