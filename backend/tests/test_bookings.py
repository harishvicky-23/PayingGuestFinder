from datetime import datetime, timedelta, timezone
import pytest
from backend.app.models.entities import BookingStatus

def test_booking_creation_and_price_calc(client, sample_property, renter_token):
    start = datetime.now(timezone.utc) + timedelta(days=2)
    end = start + timedelta(hours=3)
    
    payload = {
        "property_id": sample_property.id,
        "start_datetime": start.isoformat(),
        "end_datetime": end.isoformat(),
        "duration_type": "hourly",
        "guest_count": 1,
    }
    res = client.post(
        "/api/v1/bookings",
        json=payload,
        headers={"Authorization": f"Bearer {renter_token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "PENDING"
    # 3 hours * 300 = 900 base, 45 fee = 945 total
    assert data["base_price"] == 900.0
    assert data["fees"] == 45.0
    assert data["total_price"] == 945.0

def test_booking_exceeding_capacity_fails(client, sample_property, renter_token):
    start = datetime.now(timezone.utc) + timedelta(days=3)
    end = start + timedelta(hours=2)
    
    payload = {
        "property_id": sample_property.id,
        "start_datetime": start.isoformat(),
        "end_datetime": end.isoformat(),
        "duration_type": "hourly",
        "guest_count": 10,  # Property max is 2
    }
    res = client.post(
        "/api/v1/bookings",
        json=payload,
        headers={"Authorization": f"Bearer {renter_token}"},
    )
    assert res.status_code == 400
    assert "exceeds maximum" in res.json()["detail"]

def test_overlapping_confirmed_booking_conflict(client, sample_property, renter_token, host_token):
    start1 = datetime.now(timezone.utc) + timedelta(days=5, hours=2)
    end1 = start1 + timedelta(hours=4)
    
    # 1. Create first booking
    res1 = client.post(
        "/api/v1/bookings",
        json={
            "property_id": sample_property.id,
            "start_datetime": start1.isoformat(),
            "end_datetime": end1.isoformat(),
            "duration_type": "hourly",
            "guest_count": 1,
        },
        headers={"Authorization": f"Bearer {renter_token}"},
    )
    assert res1.status_code == 201
    b1_id = res1.json()["id"]

    # 2. Host confirms first booking
    conf_res = client.patch(
        f"/api/v1/bookings/{b1_id}/status",
        json={"status": "CONFIRMED"},
        headers={"Authorization": f"Bearer {host_token}"},
    )
    assert conf_res.status_code == 200
    assert conf_res.json()["status"] == "CONFIRMED"

    # 3. Create second booking with overlapping time window
    start2 = start1 + timedelta(hours=2)  # overlaps!
    end2 = start2 + timedelta(hours=4)
    
    res2 = client.post(
        "/api/v1/bookings",
        json={
            "property_id": sample_property.id,
            "start_datetime": start2.isoformat(),
            "end_datetime": end2.isoformat(),
            "duration_type": "hourly",
            "guest_count": 1,
        },
        headers={"Authorization": f"Bearer {renter_token}"},
    )
    assert res2.status_code == 400
    assert "overlaps with an existing confirmed booking" in res2.json()["detail"]

def test_review_lifecycle(client, sample_property, renter_token, host_token):
    # 1. Create booking
    start = datetime.now(timezone.utc) + timedelta(days=10)
    end = start + timedelta(hours=2)
    res = client.post(
        "/api/v1/bookings",
        json={
            "property_id": sample_property.id,
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat(),
            "duration_type": "hourly",
            "guest_count": 1,
        },
        headers={"Authorization": f"Bearer {renter_token}"},
    )
    b_id = res.json()["id"]

    # Trying to review pending booking should fail
    rev_fail = client.post(
        "/api/v1/reviews",
        json={"booking_id": b_id, "rating": 5.0, "review_text": "Too early"},
        headers={"Authorization": f"Bearer {renter_token}"},
    )
    assert rev_fail.status_code == 400

    # Host confirms booking
    client.patch(
        f"/api/v1/bookings/{b_id}/status",
        json={"status": "CONFIRMED"},
        headers={"Authorization": f"Bearer {host_token}"},
    )

    # Now review succeeds
    rev_ok = client.post(
        "/api/v1/reviews",
        json={"booking_id": b_id, "rating": 4.8, "review_text": "Great workspace!"},
        headers={"Authorization": f"Bearer {renter_token}"},
    )
    assert rev_ok.status_code == 201
    assert rev_ok.json()["rating"] == 4.8

    # Second review on same booking fails (duplicate prevention)
    rev_dupe = client.post(
        "/api/v1/reviews",
        json={"booking_id": b_id, "rating": 4.0, "review_text": "Duplicate"},
        headers={"Authorization": f"Bearer {renter_token}"},
    )
    assert rev_dupe.status_code == 400
    assert "already been reviewed" in rev_dupe.json()["detail"]
