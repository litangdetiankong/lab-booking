from langchain_core.tools import tool
from app.db.database import SessionLocal
from app.db.models import Lab
from app.services import equipment_service, lab_service

@tool
def search_labs(keyword: str = "", capacity_min: int = 0) -> str:
    """按名称/描述/位置关键词和最小容纳人数搜索开放中的实验室，返回编号、名称、容量、位置列表。
    当用户想找实验室或判断哪个实验室满足需求时调用它。"""
    db = SessionLocal()
    try:
        labs = lab_service.list_labs(db, keyword=keyword, capacity_min=capacity_min, status="开放中")
        return "\n".join(f"{l.id}. {l.name}｜容纳{l.capacity}人｜{l.location}" for l in labs) \
               or "没有符合条件的实验室"
    finally:
        db.close()

@tool
def get_lab_equipment(lab_name: str) -> str:
    """查询指定名称实验室的设备清单，返回设备名、型号、可用数量。
    当用户问某个实验室有什么设备，或问某类设备在哪里时调用它。"""
    db = SessionLocal()
    try:
        # 先精确匹配实验室名，找不到再模糊匹配（用户常输简称，如"AI 实验室"→"AI"）
        lab = db.query(Lab).filter(Lab.name == lab_name).first()
        if not lab:
            lab = db.query(Lab).filter(Lab.name.like(f"%{lab_name}%")).first()
        if not lab:
            return f"没有找到名为「{lab_name}」的实验室"
        # 复用步骤 7 的设备查询——AI 工具就是业务函数的薄包装
        eqs = equipment_service.list_equipment(db, lab.id)
        if not eqs:
            return f"「{lab.name}」暂无登记设备"
        lines = [f"「{lab.name}」的设备清单："]
        lines += [f"- {e.name}（{e.model}）：可用 {e.available}/{e.total}" for e in eqs]
        return "\n".join(lines)
    finally:
        db.close()