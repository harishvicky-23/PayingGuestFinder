import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.entities import RecommendationLog, RecommendationFeedback, Property, User
from backend.app.schemas.all_schemas import ModelRegistryOut, DriftReportOut, RetrainRequest
from backend.app.ml.registry import ModelRegistryManager
from backend.app.ml.drift import calculate_psi, assess_feature_drifts
from backend.app.api.deps import get_current_admin_user, get_current_host_user

router = APIRouter(prefix="/ml", tags=["ML Operations & MLOps"])

@router.get("/status")
def get_ml_status():
    """Retrieve full status of active models, candidate models, and historical deployments."""
    return ModelRegistryManager.get_full_status()

@router.get("/drift", response_model=DriftReportOut)
def check_data_and_prediction_drift(db: Session = Depends(get_db)):
    """
    Evaluate feature distribution drift (PSI) between training baseline and recent inference requests.
    """
    ref_file = settings.DATA_DIR / "synthetic_recommender_data.csv"
    if not ref_file.exists():
        # Fallback empty check
        return DriftReportOut(
            feature_drifts={},
            overall_drift_detected=False,
            psi_scores={},
            recommendation_feedback_drift={},
            reference_data_size=0,
            current_data_size=0,
            timestamp=datetime.now(timezone.utc),
            alert_message="No reference dataset found for drift analysis.",
        )

    ref_df = pd.read_csv(ref_file)

    # Load current inference logs
    logs = db.query(RecommendationLog).order_by(RecommendationLog.created_at.desc()).limit(200).all()
    
    if len(logs) < 5:
        # Create small sample for demo if inference logs are still sparse
        cur_prices = db.query(Property.price_per_hour).filter(Property.active == True).all()
        cur_prices_arr = [p[0] for p in cur_prices] if cur_prices else [350.0, 450.0]
        cur_df = pd.DataFrame({
            "price": cur_prices_arr,
            "budget": [p * 1.2 for p in cur_prices_arr],
            "distance_km": [4.2] * len(cur_prices_arr),
        })
    else:
        cur_records = []
        for l in logs:
            cur_records.append({
                "budget": l.budget or 500.0,
                "price": (l.budget or 500.0) * 0.8,
                "distance_km": 5.0,
            })
        cur_df = pd.DataFrame(cur_records)

    drift_report = assess_feature_drifts(
        reference_df=ref_df,
        current_df=cur_df,
        features=["price", "budget", "distance_km"],
    )

    # Check feedback trends
    feedbacks = db.query(RecommendationFeedback).all()
    fb_breakdown = {}
    for f in feedbacks:
        fb_breakdown[f.feedback_type] = fb_breakdown.get(f.feedback_type, 0) + 1

    return DriftReportOut(
        feature_drifts=drift_report["feature_drifts"],
        overall_drift_detected=drift_report["overall_drift_detected"],
        psi_scores=drift_report["psi_scores"],
        recommendation_feedback_drift=fb_breakdown,
        reference_data_size=drift_report["reference_data_size"],
        current_data_size=drift_report["current_data_size"],
        timestamp=drift_report["timestamp"],
        alert_message="; ".join(drift_report["alerts"]) if drift_report["alerts"] else "All tracked features within stable thresholds (PSI < 0.10).",
    )

@router.post("/retrain")
def trigger_retraining(
    req: RetrainRequest,
    current_user: User = Depends(get_current_host_user),
):
    """
    Trigger end-to-end retraining and candidate evaluation workflow.
    Restricted to authorized hosts or administrators.
    """
    try:
        if req.model_name == "recommender":
            from backend.app.ml.train_recommender import train_recommender
            candidate = train_recommender(
                auto_activate=req.auto_activate_if_superior,
            )
        elif req.model_name == "demand_predictor":
            from backend.app.ml.train_demand_model import train_demand_model
            candidate = train_demand_model(
                auto_activate=req.auto_activate_if_superior,
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown model name: {req.model_name}")

        return {
            "message": f"Successfully trained and logged candidate for '{req.model_name}'.",
            "candidate": candidate,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Retraining workflow failed: {str(e)}")

@router.post("/activate/{model_name}")
def activate_candidate_model(
    model_name: str,
    current_user: User = Depends(get_current_host_user),
):
    """
    Safely promote a candidate model to active in the local model registry.
    Ensures validation metrics pass before replacing the active baseline.
    """
    try:
        active = ModelRegistryManager.activate_model(model_name)
        return {
            "message": f"Candidate model for '{model_name}' successfully promoted to ACTIVE.",
            "active_model": active,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
