from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas import FilterOptions, LocationResolveResponse, RestaurantListResponse
from app.services.filter_options_service import get_filter_options
from app.services.ingest_service import collect_and_upsert
from app.services.location_service import parse_location_input
from app.services.query_service import query_restaurants

router = APIRouter(prefix="/api", tags=["restaurants"])


@router.get("/restaurants", response_model=RestaurantListResponse)
def list_restaurants(
    city: str = Query(default=settings.default_city),
    district: str | None = None,
    hot_spot: str | None = None,
    avg_price: int | None = None,
    tags: str | None = None,
    name: str | None = None,
    recommended_dishes: str | None = None,
    source: str | None = None,
    pet_friendly: bool | None = None,
    recent_business_district: str | None = None,
    min_rating: float | None = Query(default=settings.high_score_threshold),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_lat: float | None = None,
    user_lng: float | None = None,
    db: Session = Depends(get_db),
):
    return query_restaurants(
        db,
        city=city,
        district=district,
        hot_spot=hot_spot,
        avg_price=avg_price,
        tags=tags,
        name=name,
        recommended_dishes=recommended_dishes,
        source=source,
        pet_friendly=pet_friendly,
        recent_business_district=recent_business_district,
        min_rating=min_rating,
        page=page,
        page_size=page_size,
        user_lat=user_lat,
        user_lng=user_lng,
    )


@router.get("/filter-options", response_model=FilterOptions)
def list_filter_options(db: Session = Depends(get_db)):
    return get_filter_options(db)


@router.get("/location/resolve", response_model=LocationResolveResponse)
def resolve_location(q: str, db: Session = Depends(get_db)):  # noqa: ARG001
    try:
        label, lat, lng = parse_location_input(q)
        return LocationResolveResponse(label=label, latitude=lat, longitude=lng)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/collect")
async def collect_data(
    city: str = Query(default=settings.default_city),
    date_from: str = Query(default=settings.fetch_from),
    date_to: str = Query(default=settings.fetch_to),
    min_rating: float = Query(default=settings.high_score_threshold),
    db: Session = Depends(get_db),
):
    start = date.fromisoformat(date_from)
    end = date.fromisoformat(date_to)
    stats = await collect_and_upsert(db, city=city, start_date=start, end_date=end, min_rating=min_rating)
    return {"ok": True, "stats": stats}
