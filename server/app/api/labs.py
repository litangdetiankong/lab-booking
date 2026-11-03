from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_admin
from app.core.exceptions import BusinessError
from app.core.response import ok
from app.db.database import get_db
from app.db.models import User
from app.services import equipment_service, lab_service

router = APIRouter()

class LabIn(BaseModel):
    name: str
    description: str = ""
    location: str = ""
    capacity: int = 0
    open_time_start: str      # "09:00" 字符串，转 time 的活交给 service 层
    open_time_end: str
    status: str = "开放中"

class EquipmentIn(BaseModel):
    name: str
    model: str = ""
    total: int = 1
    available: int = 1

@router.get("")
def list_labs(keyword: str = "", capacity_min: int = 0, status: str | None = None,
              user: User = Depends(get_current_user),   # 登录即可——人员端步骤 8 也用这个接口
              db: Session = Depends(get_db)):
    labs = lab_service.list_labs(db, keyword=keyword, capacity_min=capacity_min, status=status)
    # 列表只回摘要（不含 description 长文）：带宽 + 界面噪音 + 响应模型即文档
    return ok([{"id": l.id, "name": l.name, "location": l.location,
                "capacity": l.capacity, "status": l.status} for l in labs])

@router.post("", dependencies=[Depends(require_admin)])
# dependencies=[依赖]：只要"校验通过"这个副作用，不需要把 user 传进函数体
def create_lab(data: LabIn, db: Session = Depends(get_db)):
    lab = lab_service.create_lab(db, data.model_dump())   # Pydantic v2：模型 → dict
    return ok({"id": lab.id})

@router.put("/{lab_id}", dependencies=[Depends(require_admin)])
def update_lab(lab_id: int, data: LabIn, db: Session = Depends(get_db)):
    lab = lab_service.update_lab(db, lab_id, data.model_dump())
    if not lab:
        raise BusinessError(4101, "检测室不存在")
    return ok({"id": lab.id})

@router.delete("/{lab_id}", dependencies=[Depends(require_admin)])
def delete_lab(lab_id: int, db: Session = Depends(get_db)):
    lab_service.delete_lab(db, lab_id)     # 设备随 FK CASCADE 一起删
    return ok()

# ---- 设备：挂在实验室下的子资源 ----
@router.get("/{lab_id}/equipment")
def list_equipment(lab_id: int, db: Session = Depends(get_db)):
    return ok([{"id": e.id, "name": e.name, "model": e.model,
                "total": e.total, "available": e.available}
               for e in equipment_service.list_equipment(db, lab_id)])

@router.post("/{lab_id}/equipment", dependencies=[Depends(require_admin)])
def add_equipment(lab_id: int, data: EquipmentIn, db: Session = Depends(get_db)):
    eq = equipment_service.add_equipment(db, lab_id, data.model_dump())
    return ok({"id": eq.id})

@router.put("/equipment/{eq_id}", dependencies=[Depends(require_admin)])
def update_equipment(eq_id: int, data: EquipmentIn, db: Session = Depends(get_db)):
    eq = equipment_service.update_equipment(db, eq_id, data.model_dump())
    if not eq:
        raise BusinessError(4102, "设备不存在")
    return ok({"id": eq.id})

@router.delete("/equipment/{eq_id}", dependencies=[Depends(require_admin)])
def delete_equipment(eq_id: int, db: Session = Depends(get_db)):
    equipment_service.delete_equipment(db, eq_id)
    return ok()

@router.get("/{lab_id}")
def get_lab_detail(lab_id: int, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    lab = lab_service.get_lab(db, lab_id)
    if not lab:
        raise BusinessError(4101, "检测室不存在")
    return ok({"id": lab.id, "name": lab.name, "description": lab.description,
               "location": lab.location, "capacity": lab.capacity,
               "open_time_start": lab.open_time_start.strftime("%H:%M"),
               "open_time_end": lab.open_time_end.strftime("%H:%M"),
               "status": lab.status})