import time
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.entities import Property, User
from backend.app.schemas.all_schemas import (
    RecommendationRequest, RecommendationResponse,
    RecommendationFeedbackCreate, RecommendationFeedbackOut
)
from backend.app.repositories.property_repo import PropertyRepository
from backend.app.repositories.feedback_repo import FeedbackRepository
from backend.app.utils.geo import resolve_location_coordinates
from backend.app.ml.recommender import recommender_service
from backend.app.ml.registry import ModelRegistryManager
from backend.app.api.deps import get_optional_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

def _process_recommendation(
    req: RecommendationRequest,
    db: Session,
    current_user: Optional[User],
) -> RecommendationResponse:
    start_time = time.time()
    session_id = f"sess_{uuid.uuid4().hex[:10]}"

    # 1. Resolve coordinates
    lat, lon, loc_source = resolve_location_coordinates(
        query=req.location_query,
        lat=req.latitude,
        lon=req.longitude,
    )

    # 2. Fetch active candidate properties
    all_props = PropertyRepository.list_properties(db=db, active_only=True, limit=500)

    # 3. Stage 1: Eligibility Filtering
    eligible_candidates, suggestions = recommender_service.filter_eligible_properties(
        properties=all_props,
        user_lat=lat,
        user_lon=lon,
        radius_km=req.radius_km,
        budget=req.budget,
        duration_type=req.duration_type,
        guest_count=req.guest_count,
        required_amenities=req.required_amenities,
        property_type=req.property_type,
    )

    # Fetch ratings dictionary
    property_ratings = {}
    for prop, _, _ in eligible_candidates:
        stats = PropertyRepository.get_property_rating_stats(db, prop.id)
        property_ratings[prop.id] = (stats["average_rating"], stats["review_count"])

    # 4. Model Selection & Scoring
    active_model_info = ModelRegistryManager.get_active_model_info("recommender")
    model_version = active_model_info.get("version", "v1.0.0-baseline")
    model_type = active_model_info.get("model_type", "weighted_baseline")
    artifact_path = active_model_info.get("artifact_path", "")

    if req.model_choice == "baseline" or not artifact_path:
        scored_items = recommender_service.score_and_rank_baseline(
            candidates=eligible_candidates,
            user=current_user,
            user_lat=lat,
            user_lon=lon,
            radius_km=req.radius_km,
            budget=req.budget,
            duration_type=req.duration_type,
            required_amenities=req.required_amenities,
            property_ratings=property_ratings,
        )
        final_model_type = "weighted_baseline"
    else:
        # Use ML ranker with graceful baseline fallback
        scored_items = recommender_service.score_and_rank_ml(
            candidates=eligible_candidates,
            user=current_user,
            user_lat=lat,
            user_lon=lon,
            radius_km=req.radius_km,
            budget=req.budget,
            duration_type=req.duration_type,
            required_amenities=req.required_amenities,
            property_ratings=property_ratings,
            artifact_path=artifact_path,
        )
        final_model_type = model_type

    elapsed_ms = round((time.time() - start_time) * 1000.0, 2)

    # 5. Privacy-conscious recommendation logging
    FeedbackRepository.log_recommendation(
        db=db,
        session_id=session_id,
        model_version=model_version,
        candidate_count=len(all_props),
        returned_count=len(scored_items),
        latency_ms=elapsed_ms,
        user_id=current_user.id if current_user else None,
        search_lat=lat,
        search_lon=lon,
        duration_type=req.duration_type,
        budget=req.budget,
    )

    return RecommendationResponse(
        session_id=session_id,
        model_version=model_version,
        model_type=final_model_type,
        count=len(scored_items),
        results=scored_items,
        relaxed_filter_suggestions=suggestions if len(scored_items) < 3 else None,
    )

@router.post("", response_model=RecommendationResponse)
def get_recommendations_post(
    req: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Retrieve ranked personalized recommendations via POST body."""
    return _process_recommendation(req, db, current_user)

@router.get("", response_model=RecommendationResponse)
def get_recommendations_get(
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    location: Optional[str] = Query(None, description="Neighbourhood name e.g. Guindy, Velachery"),
    duration_type: str = Query("hourly"),
    budget: Optional[float] = Query(None),
    guests: int = Query(1, ge=1),
    amenities: Optional[str] = Query(None, description="Comma-separated amenities"),
    property_type: Optional[str] = Query(None),
    radius_km: float = Query(15.0, ge=1.0, le=100.0),
    model_choice: str = Query("auto"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Retrieve ranked personalized recommendations via GET parameters."""
    req_amenities = [a.strip() for a in amenities.split(",")] if amenities else []
    req = RecommendationRequest(
        latitude=latitude,
        longitude=longitude,
        location_query=location,
        duration_type=duration_type,
        budget=budget,
        guest_count=guests,
        required_amenities=req_amenities,
        property_type=property_type,
        radius_km=radius_km,
        model_choice=model_choice,
    )
    return _process_recommendation(req, db, current_user)

@router.post("/feedback", response_model=RecommendationFeedbackOut, status_code=status.HTTP_201_CREATED)
def submit_recommendation_feedback(
    fb_in: RecommendationFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Store recommendation relevance feedback for continuous evaluation and drift monitoring."""
    fb = FeedbackRepository.create_feedback(
        db=db,
        session_id=fb_in.session_id,
        property_id=fb_in.property_id,
        feedback_type=fb_in.feedback_type,
        model_version=fb_in.model_version,
        user_id=current_user.id if current_user else None,
    )
    return RecommendationFeedbackOut.model_validate(fb)
