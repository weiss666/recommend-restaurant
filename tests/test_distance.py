from app.services.location_service import haversine_km, parse_location_input


def test_haversine_returns_reasonable_distance():
    km = haversine_km(31.2304, 121.4737, 31.2233, 121.4450)
    assert km > 2
    assert km < 4


def test_parse_location_preset():
    label, lat, lng = parse_location_input("静安寺")
    assert label == "静安寺"
    assert isinstance(lat, float)
    assert isinstance(lng, float)
