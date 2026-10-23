from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.entities import RecommendationFeedback, RecommendationLog

class FeedbackRepository:
    @staticmethod
    def create_feedback(
        db: Session,
        session_id: str,
        property_id: int,
        feedback_type: str,
        model_version: str,
        user_id: Optional[int] = None,
    ) -> RecommendationFeedback:
        fb = RecommendationFeedback(
            session_id=session_id,
            property_id=property_id,
            feedback_type=feedback_type,
            model_version=model_version,
            user_id=user_id,
        )
        db.add(fb)
        db.commit()
        db.refresh(fb)
        return fb

    @staticmethod
    def log_recommendation(
        db: Session,
        session_id: str,
        model_version: str,
        candidate_count: int,
        returned_count: int,
        latency_ms: float,
        user_id: Optional[int] = None,
        search_lat: Optional[float] = None,
        search_lon: Optional[float] = None,
        duration_type: Optional[str] = None,
        budget: Optional[float] = None,
    ) -> RecommendationLog:
        log = RecommendationLog(
            session_id=session_id,
            user_id=user_id,
            model_version=model_version,
            candidate_count=candidate_count,
            returned_count=returned_count,
            latency_ms=latency_ms,
            search_latitude=search_lat,
            search_longitude=search_lon,
            duration_type=duration_type,
            budget=budget,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
