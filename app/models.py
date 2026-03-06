from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    city: Mapped[str] = mapped_column(String(50), index=True, default="上海")
    district: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    hot_spot: Mapped[str | None] = mapped_column(String(150), index=True, nullable=True)
    avg_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma separated
    recommended_dishes: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma separated
    source: Mapped[str] = mapped_column(String(50), index=True)
    pet_friendly: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    recent_business_district: Mapped[str | None] = mapped_column(String(150), index=True, nullable=True)
    rating: Mapped[float] = mapped_column(Float, index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    crawled_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
