from __future__ import annotations

from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import Session

from app.models import Restaurant
from app.schemas import RestaurantListResponse, RestaurantOut
from app.services.location_service import haversine_km


def _contains_csv(column, value: str):
    like_value = f"%{value}%"
    return column.ilike(like_value)


def _apply_filters(
    stmt: Select,
    city: str | None,
    district: str | None,
    hot_spot: str | None,
    avg_price: int | None,
    tags: str | None,
    name: str | None,
    recommended_dishes: str | None,
    source: str | None,
    pet_friendly: bool | None,
    recent_business_district: str | None,
    min_rating: float | None,
) -> Select:
    conditions = []
    if city:
        conditions.append(Restaurant.city == city)
    if district:
        conditions.append(Restaurant.district == district)
    if hot_spot:
        conditions.append(Restaurant.hot_spot == hot_spot)
    if avg_price is not None:
        conditions.append(Restaurant.avg_price <= avg_price)
    if tags:
        conditions.append(_contains_csv(Restaurant.tags, tags))
    if name:
        conditions.append(Restaurant.name.ilike(f"%{name}%"))
    if recommended_dishes:
        conditions.append(_contains_csv(Restaurant.recommended_dishes, recommended_dishes))
    if source:
        conditions.append(Restaurant.source == source)
    if pet_friendly is not None:
        conditions.append(Restaurant.pet_friendly == pet_friendly)
    if recent_business_district:
        conditions.append(Restaurant.recent_business_district == recent_business_district)
    if min_rating is not None:
        conditions.append(Restaurant.rating >= min_rating)

    if conditions:
        stmt = stmt.where(and_(*conditions))
    return stmt


def query_restaurants(
    db: Session,
    *,
    city: str | None = None,
    district: str | None = None,
    hot_spot: str | None = None,
    avg_price: int | None = None,
    tags: str | None = None,
    name: str | None = None,
    recommended_dishes: str | None = None,
    source: str | None = None,
    pet_friendly: bool | None = None,
    recent_business_district: str | None = None,
    min_rating: float | None = None,
    page: int = 1,
    page_size: int = 20,
    user_lat: float | None = None,
    user_lng: float | None = None,
) -> RestaurantListResponse:
    stmt = select(Restaurant)
    stmt = _apply_filters(
        stmt,
        city,
        district,
        hot_spot,
        avg_price,
        tags,
        name,
        recommended_dishes,
        source,
        pet_friendly,
        recent_business_district,
        min_rating,
    )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(Restaurant.rating.desc(), Restaurant.id.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(stmt).all()

    result_items: list[RestaurantOut] = []
    for row in rows:
        item = RestaurantOut(
            id=row.id,
            name=row.name,
            city=row.city,
            district=row.district,
            hot_spot=row.hot_spot,
            avg_price=row.avg_price,
            tags=[x.strip() for x in (row.tags or "").split(",") if x.strip()],
            recommended_dishes=[x.strip() for x in (row.recommended_dishes or "").split(",") if x.strip()],
            source=row.source,
            pet_friendly=row.pet_friendly,
            recent_business_district=row.recent_business_district,
            rating=row.rating,
            latitude=row.latitude,
            longitude=row.longitude,
            address=row.address,
            crawled_at=row.crawled_at,
            distance_km=None,
        )
        if (
            user_lat is not None
            and user_lng is not None
            and row.latitude is not None
            and row.longitude is not None
        ):
            item.distance_km = haversine_km(user_lat, user_lng, row.latitude, row.longitude)
        result_items.append(item)

    return RestaurantListResponse(total=total, page=page, page_size=page_size, items=result_items)
