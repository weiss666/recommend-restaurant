from __future__ import annotations

import math

LOCATION_PRESETS: dict[str, tuple[float, float]] = {
    "人民广场": (31.2304, 121.4737),
    "陆家嘴": (31.2397, 121.4998),
    "静安寺": (31.2233, 121.4450),
    "徐家汇": (31.1947, 121.4374),
    "虹桥": (31.2000, 121.3200),
}


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius_km = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(radius_km * c, 2)


def parse_location_input(raw: str) -> tuple[str, float, float]:
    value = raw.strip()
    if not value:
        raise ValueError("location is empty")

    if value in LOCATION_PRESETS:
        lat, lng = LOCATION_PRESETS[value]
        return value, lat, lng

    parts = [x.strip() for x in value.split(",")]
    if len(parts) == 2:
        lat = float(parts[0])
        lng = float(parts[1])
        return f"{lat:.4f},{lng:.4f}", lat, lng

    raise ValueError("location format must be 'lat,lng' or known place name")
