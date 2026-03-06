from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from app.schemas import RestaurantIn


class BaseCollector(ABC):
    @abstractmethod
    async def fetch(self, city: str, start_date: date, end_date: date) -> list[RestaurantIn]:
        raise NotImplementedError
