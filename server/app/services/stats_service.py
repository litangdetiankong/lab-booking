from datetime import date
from sqlalchemy.orm import Session
from app.db.models import Lab, Reservation

def get_stats(db: Session, user_id: int, is_admin: bool) -> dict:
    """取舍说明：四条 count 简单直白、每条都走索引，学习项目毫秒级完成；
    数据量大了再合并成一条聚合 SQL 或加汇总表——不要过早优化"""
    my_total = db.query(Reservation).filter(
        Reservation.user_id == user_id).count()          # 我的预约总数
    upcoming = db.query(Reservation).filter(
        Reservation.user_id == user_id,
        Reservation.date >= date.today(),                # 今天及以后
        Reservation.status == "approved").count()        # 已通过才算"即将开始"
    lab_total = db.query(Lab).count()
    # 待审核数只对管理员有意义——普通用户给 None，前端不渲染这张卡
    pending = (db.query(Reservation).filter(Reservation.status == "pending").count()
               if is_admin else None)
    return {"my_total": my_total, "upcoming": upcoming,
            "lab_total": lab_total, "pending": pending}