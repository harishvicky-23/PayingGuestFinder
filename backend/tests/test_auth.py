import pytest
from backend.app.core.security import verify_password, get_password_hash

def test_password_hashing():
    raw = "securepassword123"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_user_registration(client):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "mypassword123",
            "role": "renter",
            "preferred_budget": 600.0,
            "preferred_amenities": ["wifi"],
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["role"] == "renter"

def test_duplicate_registration_fails(client):
    payload = {
        "name": "Duplicate User",
        "email": "dupe@example.com",
        "password": "mypassword123",
        "role": "renter",
    }
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"]

def test_login_success(client, sample_users):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "testrenter@example.com", "password": "password123"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["name"] == "Test Renter"

def test_login_wrong_password(client, sample_users):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "testrenter@example.com", "password": "wrongpassword"},
    )
    assert res.status_code == 401

def test_get_me_endpoint(client, renter_token):
    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {renter_token}"},
    )
    assert res.status_code == 200
    assert res.json()["email"] == "testrenter@example.com"

def test_unauthenticated_me_fails(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
