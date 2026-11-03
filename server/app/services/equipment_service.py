from app.core.exceptions import BusinessError
from app.db.models import Equipment

def list_equipment(db, lab_id: int) -> list[Equipment]:
    return db.query(Equipment).filter(Equipment.lab_id == lab_id).all()

def add_equipment(db, lab_id: int, data: dict) -> Equipment:
    # available ≤ total 是跨字段校验，数据库的简单约束做不到，放 service 层
    if data["available"] > data["total"]:
        raise BusinessError(4001, "可用数量不能大于总数")
    eq = Equipment(lab_id=lab_id, **data)
    db.add(eq); db.commit(); db.refresh(eq)
    return eq

def update_equipment(db, eq_id: int, data: dict) -> Equipment | None:
    eq = db.get(Equipment, eq_id)
    if not eq:
        return None
    total = data.get("total", eq.total)          # 没传就用现值——跨字段校验要算"改完之后"的值
    available = data.get("available", eq.available)
    if available > total:
        raise BusinessError(4001, "可用数量不能大于总数")
    for k, v in data.items():
        setattr(eq, k, v)
    db.commit()
    return eq

def delete_equipment(db, eq_id: int) -> None:
    eq = db.get(Equipment, eq_id)
    if eq:
        db.delete(eq); db.commit()