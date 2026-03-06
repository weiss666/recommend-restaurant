from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Restaurant Finder")
    db_url: str = os.getenv("DB_URL", "sqlite:///./data.db")
    default_city: str = os.getenv("DEFAULT_CITY", "上海")
    high_score_threshold: float = float(os.getenv("HIGH_SCORE_THRESHOLD", "4.5"))
    fetch_from: str = os.getenv("FETCH_FROM", "2025-09-06")
    fetch_to: str = os.getenv("FETCH_TO", "2026-03-06")
    aggregator_api_key: str = os.getenv("AGGREGATOR_API_KEY", "")
    aggregator_base_url: str = os.getenv("AGGREGATOR_BASE_URL", "https://example-aggregator.invalid")

    def fetch_range(self) -> tuple[date, date]:
        return date.fromisoformat(self.fetch_from), date.fromisoformat(self.fetch_to)


settings = Settings()
