from datetime import datetime, timezone, timedelta
import pytest
from backend.app.utils.geo import haversine_distance, resolve_location_coordinates
from backend.app.utils.pricing import calculate_duration_hours, calculate_rental_price

def test_haversine_distance():
    # Distance between Guindy (13.0067, 80.2025) and Velachery (12.9756, 80.2206) is ~3.9 km
    dist = haversine_distance(13.0067, 80.2025, 12.9756, 80.2206)
    assert 3.0 < dist < 5.0
    
    # Distance from point to itself is 0
    assert haversine_distance(13.0067, 80.2025, 13.0067, 80.2025) == 0.0

def test_resolve_location():
    # Known neighbourhood lookup
    lat, lon, name = resolve_location_coordinates("Guindy")
    assert lat is not None
    assert lon is not None
    assert name == "Guindy"

    # Explicit coordinates
    lat2, lon2, src = resolve_location_coordinates(lat=13.05, lon=80.25)
    assert lat2 == 13.05
    assert lon2 == 80.25

def test_duration_hours_calculation():
    now = datetime.now(timezone.utc)
    after_3h = now + timedelta(hours=3, minutes=30)
    hrs = calculate_duration_hours(now, after_3h)
    assert hrs == 3.5

    # Reverse order raises ValueError
    with pytest.raises(ValueError):
        calculate_duration_hours(after_3h, now)

def test_pricing_calculation():
    # Hourly: 3 hours @ 200/hr = 600 base + 30 fee = 630 total
    p_hourly = calculate_rental_price(
        duration_type="hourly",
        duration_hours=3.0,
        price_per_hour=200.0,
        price_per_half_day=800.0,
        price_per_day=1500.0,
    )
    assert p_hourly["base_price"] == 600.0
    assert p_hourly["fees"] == 30.0
    assert p_hourly["total_price"] == 630.0

    # Half day block
    p_half = calculate_rental_price(
        duration_type="half_day",
        duration_hours=6.0,
        price_per_hour=200.0,
        price_per_half_day=800.0,
        price_per_day=1500.0,
    )
    assert p_half["base_price"] == 800.0
    assert p_half["fees"] == 40.0
    assert p_half["total_price"] == 840.0
