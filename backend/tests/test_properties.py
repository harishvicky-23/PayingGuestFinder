import pytest

def test_list_properties(client, sample_property):
    res = client.get("/api/v1/properties")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    # Check that exact_address is not exposed in public list
    assert "exact_address" not in data[0]

def test_filter_properties(client, sample_property):
    # Match neighbourhood
    res = client.get("/api/v1/properties?neighbourhood=Guindy")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Unmatched neighbourhood
    res2 = client.get("/api/v1/properties?neighbourhood=NonExistentArea")
    assert res2.status_code == 200
    assert len(res2.json()) == 0

def test_host_create_property(client, host_token):
    payload = {
        "title": "New Host Studio",
        "description": "Clean and quiet workspace in Velachery.",
        "property_type": "workspace_studio",
        "neighbourhood": "Velachery",
        "latitude": 12.9756,
        "longitude": 80.2206,
        "public_location_description": "Near Velachery Station",
        "exact_address": "456 Private Street, Velachery",
        "price_per_hour": 250.0,
        "price_per_half_day": 950.0,
        "price_per_day": 1800.0,
        "maximum_guests": 2,
        "amenities": ["wifi", "air_conditioning"],
        "supported_durations": ["hourly", "half_day"],
    }
    res = client.post(
        "/api/v1/properties",
        json=payload,
        headers={"Authorization": f"Bearer {host_token}"},
    )
    assert res.status_code == 201
    assert res.json()["title"] == "New Host Studio"

def test_renter_cannot_create_property(client, renter_token):
    payload = {
        "title": "Unauthorized Listing",
        "description": "Should fail.",
        "property_type": "workspace_studio",
        "neighbourhood": "Guindy",
        "latitude": 13.0,
        "longitude": 80.2,
        "public_location_description": "Near Metro",
        "exact_address": "Secret address",
        "price_per_hour": 300.0,
        "price_per_half_day": 1200.0,
        "price_per_day": 2000.0,
    }
    res = client.post(
        "/api/v1/properties",
        json=payload,
        headers={"Authorization": f"Bearer {renter_token}"},
    )
    assert res.status_code == 403

def test_get_property_address_protection(client, sample_property, renter_token, host_token):
    # Public / Renter without booking -> address is None
    res_public = client.get(f"/api/v1/properties/{sample_property.id}")
    assert res_public.status_code == 200
    assert res_public.json()["exact_address"] is None

    # Host of property -> address is revealed
    res_host = client.get(
        f"/api/v1/properties/{sample_property.id}",
        headers={"Authorization": f"Bearer {host_token}"},
    )
    assert res_host.status_code == 200
    assert res_host.json()["exact_address"] == sample_property.exact_address
