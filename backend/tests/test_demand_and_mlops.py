import pytest
import pandas as pd
import numpy as np
from backend.app.ml.data_validation import validate_recommender_training_data, validate_demand_training_data
from backend.app.ml.drift import calculate_psi
from backend.app.ml.registry import ModelRegistryManager

def test_data_validation_recommender():
    valid_df = pd.DataFrame({
        "session_id": ["s1", "s2"],
        "property_id": [1, 2],
        "distance_km": [2.5, 4.0],
        "price": [300.0, 450.0],
        "budget": [500.0, 500.0],
        "rating": [4.5, 4.2],
        "amenity_match_ratio": [0.8, 0.5],
        "relevance_label": [1, 0],
    })
    ok, errs = validate_recommender_training_data(valid_df)
    assert ok is True
    assert len(errs) == 0

    # Negative price error
    invalid_df = valid_df.copy()
    invalid_df.loc[0, "price"] = -50.0
    bad, bad_errs = validate_recommender_training_data(invalid_df)
    assert bad is False
    assert any("negative" in e.lower() for e in bad_errs)

def test_data_validation_demand():
    valid_demand = pd.DataFrame({
        "neighbourhood": ["Guindy"],
        "date": ["2026-08-01"],
        "day_of_week": [4],
        "time_slot": ["evening"],
        "available_listings": [15],
        "avg_price": [400.0],
        "historical_requests": [12],
        "actual_requests": [14],
    })
    ok, errs = validate_demand_training_data(valid_demand)
    assert ok is True

    # Invalid time slot
    bad_demand = valid_demand.copy()
    bad_demand.loc[0, "time_slot"] = "midnight"
    bad, bad_errs = validate_demand_training_data(bad_demand)
    assert bad is False

def test_psi_calculation():
    # Identical distributions -> PSI = 0.0
    arr1 = np.random.normal(50, 10, 500)
    arr2 = arr1.copy()
    psi_same = calculate_psi(arr1, arr2)
    assert psi_same == 0.0

    # Shifted distribution -> PSI > 0
    arr3 = np.random.normal(70, 15, 500)
    psi_shifted = calculate_psi(arr1, arr3)
    assert psi_shifted > 0.1

def test_demand_analytics_endpoint(client):
    res = client.get("/api/v1/analytics/demand?neighbourhood=Guindy")
    assert res.status_code == 200
    data = res.json()
    assert "forecasts" in data
    assert len(data["forecasts"]) >= 4  # morning, afternoon, evening, night
    first_f = data["forecasts"][0]
    assert first_f["neighbourhood"] == "Guindy"
    assert "predicted_demand_score" in first_f
    assert "confidence_interval_low" in first_f
    assert "confidence_interval_high" in first_f
    assert first_f["confidence_interval_high"] >= first_f["confidence_interval_low"]

def test_ml_status_endpoint(client):
    res = client.get("/api/v1/ml/status")
    assert res.status_code == 200
    data = res.json()
    assert "active_models" in data
    assert "recommender" in data["active_models"]
    assert "demand_predictor" in data["active_models"]

def test_drift_endpoint(client):
    res = client.get("/api/v1/ml/drift")
    assert res.status_code == 200
    data = res.json()
    assert "feature_drifts" in data
    assert "overall_drift_detected" in data
