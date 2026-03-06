from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class RestaurantIn(BaseModel):
    name: str
    city: str = "上海"
    district: str | None = None
    hot_spot: str | None = None
    avg_price: int | None = None
    tags: list[str] = Field(default_factory=list)
    recommended_dishes: list[str] = Field(default_factory=list)
    source: str
    pet_friendly: bool = False
    recent_business_district: str | None = None
    rating: float
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None
    crawled_at: date | None = None


class RestaurantOut(BaseModel):
    id: int
    name: str
    city: str
    district: str | None = None
    hot_spot: str | None = None
    avg_price: int | None = None
    tags: list[str]
    recommended_dishes: list[str]
    source: str
    pet_friendly: bool
    recent_business_district: str | None = None
    rating: float
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None
    crawled_at: date | None = None
    distance_km: float | None = None

    model_config = {"from_attributes": True}


class RestaurantListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RestaurantOut]


class FilterOptions(BaseModel):
    city: list[str]
    district: list[str]
    hot_spot: list[str]
    avg_price: list[int]
    tags: list[str]
    name: list[str]
    recommended_dishes: list[str]
    source: list[str]
    pet_friendly: list[bool]
    recent_business_district: list[str]


class LocationResolveResponse(BaseModel):
    label: str
    latitude: float
    longitude: float
