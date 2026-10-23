import pytest
from backend.app.ml.metrics import (
    calculate_precision_at_k, calculate_recall_at_k, 
    calculate_ndcg_at_k, calculate_hit_rate_at_k
)

def test_recommendation_ranking_metrics():
    # Synthetic ground truth relevance and model scores
    y_true = [1, 0, 1, 0, 0]
    y_scores = [0.9, 0.8, 0.4, 0.2, 0.1]
    
    # In top 2: 1 relevant item (item 0) out of 2 -> precision is 0.5
    p2 = calculate_precision_at_k(y_true, y_scores, k=2)
    assert p2 == 0.5

    # Recall at 3: 2 relevant total, top 3 contains items 0, 1, 2 (items 0 and 2 are relevant -> 2/2 = 1.0)
    r3 = calculate_recall_at_k(y_true, y_scores, k=3)
    assert r3 == 1.0

    # NDCG@3 is positive and <= 1.0
    ndcg = calculate_ndcg_at_k(y_true, y_scores, k=3)
    assert 0.0 < ndcg <= 1.0

    # Hit Rate@1 is 1.0 since item 0 is relevant
    hit1 = calculate_hit_rate_at_k(y_true, y_scores, k=1)
    assert hit1 == 1.0

def test_recommendations_endpoint(client, sample_property):
    # Query within Guindy area
    res = client.post(
        "/api/v1/recommendations",
        json={
            "latitude": 13.0067,
            "longitude": 80.2025,
            "radius_km": 10.0,
            "duration_type": "hourly",
            "budget": 1000.0,
            "guest_count": 1,
            "required_amenities": ["wifi"],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert len(data["results"]) >= 1
    
    first_item = data["results"][0]
    assert "score" in first_item
    assert "component_scores" in first_item
    assert "explanations" in first_item
    assert len(first_item["explanations"]) > 0
    # Check that explanation contains distance or budget
    combined_exp = " ".join(first_item["explanations"])
    assert "budget" in combined_exp.lower() or "km" in combined_exp.lower()

def test_recommendation_filtering_out_of_radius(client, sample_property):
    # Query very far away with tight radius
    res = client.post(
        "/api/v1/recommendations",
        json={
            "latitude": 15.0,  # Far north
            "longitude": 82.0,
            "radius_km": 2.0,
            "duration_type": "hourly",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) == 0
    assert data["relaxed_filter_suggestions"] is not None

def test_recommendation_feedback(client, sample_property):
    res = client.post(
        "/api/v1/recommendations/feedback",
        json={
            "session_id": "test_session_123",
            "property_id": sample_property.id,
            "feedback_type": "relevant",
            "model_version": "v1.0.0",
        },
    )
    assert res.status_code == 201
    assert res.json()["feedback_type"] == "relevant"
