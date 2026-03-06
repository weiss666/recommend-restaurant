from __future__ import annotations

from datetime import date

import httpx

from app.collectors.base import BaseCollector
from app.config import settings
from app.schemas import RestaurantIn


class AggregatorCollector(BaseCollector):
    async def fetch(self, city: str, start_date: date, end_date: date) -> list[RestaurantIn]:
        if not settings.aggregator_api_key:
            return _sample_data(city)

        headers = {"Authorization": f"Bearer {settings.aggregator_api_key}"}
        params = {
            "city": city,
            "date_from": start_date.isoformat(),
            "date_to": end_date.isoformat(),
            "min_rating": settings.high_score_threshold,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(settings.aggregator_base_url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()

        items = payload.get("items", [])
        restaurants: list[RestaurantIn] = []
        for item in items:
            restaurants.append(
                RestaurantIn(
                    name=item.get("name", "").strip(),
                    city=item.get("city", city),
                    district=item.get("district"),
                    hot_spot=item.get("hot_spot"),
                    avg_price=item.get("avg_price"),
                    tags=item.get("tags", []),
                    recommended_dishes=item.get("recommended_dishes", []),
                    source=item.get("source", "aggregator"),
                    pet_friendly=bool(item.get("pet_friendly", False)),
                    recent_business_district=item.get("recent_business_district"),
                    rating=float(item.get("rating", 0)),
                    latitude=item.get("latitude"),
                    longitude=item.get("longitude"),
                    address=item.get("address"),
                    crawled_at=date.fromisoformat(item["crawled_at"]) if item.get("crawled_at") else None,
                )
            )
        return restaurants


def _sample_data(city: str) -> list[RestaurantIn]:
    return [
        RestaurantIn(
            name="福和面馆",
            city=city,
            district="黄浦区",
            hot_spot="人民广场",
            avg_price=58,
            tags=["本帮菜", "面馆"],
            recommended_dishes=["黄鱼面", "葱油拌面"],
            source="sample_aggregator",
            pet_friendly=False,
            recent_business_district="南京东路商圈",
            rating=4.7,
            latitude=31.2325,
            longitude=121.4733,
            address="黄浦区九江路100号",
            crawled_at=date(2026, 2, 11),
        ),
        RestaurantIn(
            name="山海炭火烧鸟",
            city=city,
            district="静安区",
            hot_spot="静安寺",
            avg_price=168,
            tags=["日料", "烧鸟"],
            recommended_dishes=["鸡牡蛎", "提灯"],
            source="sample_aggregator",
            pet_friendly=True,
            recent_business_district="静安寺商圈",
            rating=4.8,
            latitude=31.2230,
            longitude=121.4467,
            address="静安区愚园路220号",
            crawled_at=date(2026, 1, 22),
        ),
        RestaurantIn(
            name="江南小院",
            city=city,
            district="徐汇区",
            hot_spot="徐家汇",
            avg_price=132,
            tags=["江浙菜", "家庭聚餐"],
            recommended_dishes=["清蒸白鱼", "响油鳝糊"],
            source="sample_aggregator",
            pet_friendly=True,
            recent_business_district="徐家汇商圈",
            rating=4.6,
            latitude=31.1941,
            longitude=121.4372,
            address="徐汇区虹桥路90号",
            crawled_at=date(2025, 12, 15),
        ),
        RestaurantIn(
            name="潮汕牛肉研究所",
            city=city,
            district="浦东新区",
            hot_spot="陆家嘴",
            avg_price=146,
            tags=["火锅", "潮汕牛肉"],
            recommended_dishes=["吊龙", "胸口朥"],
            source="sample_aggregator",
            pet_friendly=False,
            recent_business_district="陆家嘴商圈",
            rating=4.9,
            latitude=31.2392,
            longitude=121.4996,
            address="浦东新区银城中路188号",
            crawled_at=date(2026, 2, 28),
        ),
        RestaurantIn(
            name="梧桐法式小馆",
            city=city,
            district="长宁区",
            hot_spot="虹桥",
            avg_price=220,
            tags=["法餐", "约会"],
            recommended_dishes=["油封鸭腿", "焦糖布丁"],
            source="sample_aggregator",
            pet_friendly=True,
            recent_business_district="虹桥商圈",
            rating=4.5,
            latitude=31.1992,
            longitude=121.3220,
            address="长宁区遵义南路50号",
            crawled_at=date(2025, 10, 4),
        ),
    ]
