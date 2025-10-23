# src/shared/models/schedule_models.py

from __future__ import annotations
import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.core.database import Base
import ulid

class Shift(Base):
    """
    V6 新增：排班表
    用于指定一个技师在什么时间、什么地点工作
    """
    __tablename__ = "shifts"

    uid: Mapped[str] = mapped_column(String(26), primary_key=True, default=lambda: str(ulid.new()), index=True)
    
    # 关联到 User (技师)
    technician_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.uid"), index=True)
    
    # 关联到 Location (地点)
    location_id: Mapped[str] = mapped_column(String(26), ForeignKey("locations.uid"), index=True)

    start_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="排班开始时间")
    end_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="排班结束时间")

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- Relationships (使用字符串前向引用) ---
    
    # 关联到技师 (User)
    technician: Mapped["User"] = relationship(
        "User", 
        back_populates="shifts"
    )
    
    # 关联到地点 (Location)
    location: Mapped["Location"] = relationship(
        "Location", 
        back_populates="shifts"
    )