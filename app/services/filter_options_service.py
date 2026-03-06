from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Restaurant
from app.schemas import FilterOptions


def _split_and_collect(values: list[str | None]) -> list[str]:
    items: set[str] = set()
    for value in values:
        if not value:
            continue
        parts = [x.strip() for x in value.split(",")]
        for p in parts:
            if p:
                items.add(p)
    return sorted(items)


def get_filter_options(db: Session) -> FilterOptions:
    rows = db.scalars(select(Restaurant)).all()

    city = sorted({r.city for r in rows if r.city})
    district = sorted({r.district for r in rows if r.district})
    hot_spot = sorted({r.hot_spot for r in rows if r.hot_spot})
    avg_price = sorted({r.avg_price for r in rows if r.avg_price is not None})
    name = sorted({r.name for r in rows if r.name})
    source = sorted({r.source for r in rows if r.source})
    recent_business_district = sorted(
        {r.recent_business_district for r in rows if r.recent_business_district}
    )
    tags = _split_and_collect([r.tags for r in rows])
    recommended_dishes = _split_and_collect([r.recommended_dishes for r in rows])

    return FilterOptions(
        city=city,
        district=district,
        hot_spot=hot_spot,
        avg_price=avg_price,
        tags=tags,
        name=name,
        recommended_dishes=recommended_dishes,
        source=source,
        pet_friendly=[True, False],
        recent_business_district=recent_business_district,
    )
