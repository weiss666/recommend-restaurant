from __future__ import annotations

import argparse
import asyncio
from datetime import date

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Restaurant  # noqa: F401
from app.services.ingest_service import collect_and_upsert


async def main():
    parser = argparse.ArgumentParser(description="Fetch and upsert high score restaurants")
    parser.add_argument("--city", default=settings.default_city)
    parser.add_argument("--from", dest="date_from", default=settings.fetch_from)
    parser.add_argument("--to", dest="date_to", default=settings.fetch_to)
    parser.add_argument("--min-rating", type=float, default=settings.high_score_threshold)
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        stats = await collect_and_upsert(
            db,
            city=args.city,
            start_date=date.fromisoformat(args.date_from),
            end_date=date.fromisoformat(args.date_to),
            min_rating=args.min_rating,
        )
    print(stats)


if __name__ == "__main__":
    asyncio.run(main())
