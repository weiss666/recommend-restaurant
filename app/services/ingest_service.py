from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collectors.aggregator_provider import AggregatorCollector
from app.models import Restaurant
from app.schemas import RestaurantIn


def _normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def _dedupe_key(item: RestaurantIn) -> str:
    return f"{_normalize_text(item.name)}|{_normalize_text(item.address)}|{_normalize_text(item.district)}"


def _merge_csv(existing: str | None, incoming: list[str]) -> str:
    seen = {x.strip() for x in (existing or "").split(",") if x.strip()}
    for value in incoming:
        stripped = value.strip()
        if stripped:
            seen.add(stripped)
    return ",".join(sorted(seen))


async def collect_and_upsert(
    db: Session,
    city: str,
    start_date: date,
    end_date: date,
    min_rating: float,
) -> dict[str, int]:
    collector = AggregatorCollector()
    items = await collector.fetch(city, start_date, end_date)
    items = [item for item in items if item.rating >= min_rating]

    created = 0
    updated = 0
    seen_keys: set[str] = set()

    for item in items:
        key = _dedupe_key(item)
        if key in seen_keys:
            continue
        seen_keys.add(key)

        existing = db.scalar(
            select(Restaurant).where(
                Restaurant.name == item.name,
                Restaurant.city == item.city,
                Restaurant.address == item.address,
            )
        )
        if existing is None:
            record = Restaurant(
                name=item.name,
                city=item.city,
                district=item.district,
                hot_spot=item.hot_spot,
                avg_price=item.avg_price,
                tags=",".join(item.tags),
                recommended_dishes=",".join(item.recommended_dishes),
                source=item.source,
                pet_friendly=item.pet_friendly,
                recent_business_district=item.recent_business_district,
                rating=item.rating,
                latitude=item.latitude,
                longitude=item.longitude,
                address=item.address,
                crawled_at=item.crawled_at,
            )
            db.add(record)
            created += 1
        else:
            existing.rating = max(existing.rating, item.rating)
            existing.avg_price = item.avg_price or existing.avg_price
            existing.tags = _merge_csv(existing.tags, item.tags)
            existing.recommended_dishes = _merge_csv(existing.recommended_dishes, item.recommended_dishes)
            existing.pet_friendly = existing.pet_friendly or item.pet_friendly
            existing.hot_spot = item.hot_spot or existing.hot_spot
            existing.recent_business_district = item.recent_business_district or existing.recent_business_district
            existing.latitude = item.latitude or existing.latitude
            existing.longitude = item.longitude or existing.longitude
            existing.crawled_at = item.crawled_at or existing.crawled_at
            updated += 1

    db.commit()
    return {"fetched": len(items), "created": created, "updated": updated}
