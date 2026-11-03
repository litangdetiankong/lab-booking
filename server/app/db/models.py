from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from datetime import time
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50),unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str] = mapped_column(String(50))
    avatar: Mapped[str] = mapped_column(String(255), default="")
    role: Mapped[str] = mapped_column(String(20), default="employee")

class Lab(Base):
    __tablename__ = "labs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String(100), default="")
    capacity: Mapped[int] = mapped_column(default=0)            # 可容纳人数
    open_time_start: Mapped[time] = mapped_column()             # 开放时段起
    open_time_end: Mapped[time] = mapped_column()               # 开放时段止
    status: Mapped[str] = mapped_column(String(20), default="开放中")  # 开放中 | 维护中

    equipment: Mapped[list["Equipment"]] = relationship(
        back_populates="lab", cascade="all, delete-orphan")

class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lab_id: Mapped[int] = mapped_column(ForeignKey("labs.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100), default="")
    total: Mapped[int] = mapped_column(default=1)
    available: Mapped[int] = mapped_column(default=1)

    lab: Mapped["Lab"] = relationship(back_populates="equipment")

from datetime import date, datetime, time
from sqlalchemy import Date, DateTime, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column

class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    lab_id: Mapped[int] = mapped_column(ForeignKey("labs.id"), index=True)
    date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    purpose: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    review_comment: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)