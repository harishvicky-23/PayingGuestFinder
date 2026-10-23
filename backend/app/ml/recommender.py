import os
import joblib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.entities import Property, User, Booking
from backend.app.schemas.all_schemas import RecommendationItem, RecommendationResponse
from backend.app.utils.geo import haversine_distance, resolve_location_coordinates
from backend.app.utils.pricing import calculate_rental_price
from backend.app.ml.registry import ModelRegistryManager

class RecommenderService:
    def __init__(self):
        self._cached_model = None
        self._cached_model_path = None

    def _load_ml_model(self, artifact_path: str):
        if self._cached_model_path == artifact_path and self._cached_model is not None:
            return self._cached_model
        
        path = Path(artifact_path)
        if path.exists():
            try:
                self._cached_model = joblib.load(path)
                self._cached_model_path = artifact_path
                return self._cached_model
            except Exception as e:
                print(f"[WARN] Failed to load ML model from {artifact_path}: {e}")
                return None
        return None

    def filter_eligible_properties(
        self,
        properties: List[Property],
        user_lat: Optional[float],
        user_lon: Optional[float],
        radius_km: float,
        budget: Optional[float],
        duration_type: str,
        guest_count: int,
        required_amenities: List[str],
        property_type: Optional[str] = None,
    ) -> Tuple[List[Tuple[Property, Optional[float], Dict[str, float]]], List[str]]:
        """
        Stage 1: Eligibility Filtering.
        Returns:
            eligible_candidates: List of (Property, distance_km, price_info)
            relaxed_filter_suggestions: List of suggestions if count is 0 or low
        """
        eligible = []
        rejected_reasons = {
            "budget": 0,
            "distance": 0,
            "capacity": 0,
            "duration": 0,
            "amenities": 0,
            "type": 0,
        }

        req_amenities_set = set(a.lower().strip() for a in required_amenities) if required_amenities else set()

        for prop in properties:
            if not prop.active:
                continue

            # 1. Capacity filter
            if prop.maximum_guests < guest_count:
                rejected_reasons["capacity"] += 1
                continue

            # 2. Duration filter
            if prop.supported_durations and duration_type not in prop.supported_durations:
                rejected_reasons["duration"] += 1
                continue

            # 3. Property type filter (if specific type requested)
            if property_type and property_type != "all" and prop.property_type != property_type:
                rejected_reasons["type"] += 1
                continue

            # 4. Amenities filter (strict requirement)
            if req_amenities_set:
                prop_amenities = set(a.lower().strip() for a in (prop.amenities or []))
                if not req_amenities_set.issubset(prop_amenities):
                    rejected_reasons["amenities"] += 1
                    continue

            # 5. Distance filter
            dist_km: Optional[float] = None
            if user_lat is not None and user_lon is not None:
                dist_km = haversine_distance(user_lat, user_lon, prop.latitude, prop.longitude)
                if dist_km > radius_km:
                    rejected_reasons["distance"] += 1
                    continue

            # 6. Price calculation & Budget check
            # For hourly, assume 2 hrs base comparison; for half-day 6 hrs, full-day 24 hrs
            nominal_hours = 2.0 if duration_type == "hourly" else (6.0 if duration_type == "half_day" else 24.0)
            price_info = calculate_rental_price(
                duration_type=duration_type,
                duration_hours=nominal_hours,
                price_per_hour=prop.price_per_hour,
                price_per_half_day=prop.price_per_half_day,
                price_per_day=prop.price_per_day,
            )

            if budget is not None and price_info["total_price"] > (budget * 1.15):
                # allow 15% margin or strict
                rejected_reasons["budget"] += 1
                continue

            eligible.append((prop, dist_km, price_info))

        suggestions = []
        if len(eligible) < 3:
            if rejected_reasons["distance"] > 0:
                suggestions.append(f"Expand search radius from {radius_km} km to {radius_km + 10} km.")
            if rejected_reasons["budget"] > 0 and budget is not None:
                suggestions.append(f"Increase budget from ₹{budget} to ₹{int(budget * 1.3)}.")
            if rejected_reasons["amenities"] > 0:
                suggestions.append("Relax some required amenity filters.")
            if rejected_reasons["type"] > 0:
                suggestions.append("Select 'All Property Types' to see more options.")

        return eligible, suggestions

    def score_and_rank_baseline(
        self,
        candidates: List[Tuple[Property, Optional[float], Dict[str, float]]],
        user: Optional[User],
        user_lat: Optional[float],
        user_lon: Optional[float],
        radius_km: float,
        budget: Optional[float],
        duration_type: str,
        required_amenities: List[str],
        property_ratings: Dict[int, Tuple[float, int]],
    ) -> List[RecommendationItem]:
        """
        Stage 3: Weighted Ranking Baseline with Explainable Feature Attributions.
        """
        results: List[RecommendationItem] = []
        req_amenities_set = set(a.lower().strip() for a in required_amenities) if required_amenities else set()

        for prop, dist_km, price_info in candidates:
            # 1. Proximity score (0 to 1)
            if dist_km is not None and radius_km > 0:
                loc_score = max(0.0, 1.0 - (dist_km / radius_km))
            else:
                loc_score = 0.5  # neutral if location not given

            # 2. Price suitability (0 to 1)
            calc_price = price_info["total_price"]
            if budget is not None and budget > 0:
                if calc_price <= budget:
                    price_score = 1.0 - (calc_price / (budget * 2.0))
                else:
                    price_score = max(0.0, 1.0 - ((calc_price - budget) / budget))
            else:
                price_score = 0.6

            # 3. Amenity match score (0 to 1)
            prop_amenities = set(a.lower().strip() for a in (prop.amenities or []))
            if req_amenities_set:
                matched_count = len(req_amenities_set.intersection(prop_amenities))
                amenity_score = matched_count / len(req_amenities_set)
            else:
                amenity_score = min(1.0, len(prop_amenities) / 6.0)

            # 4. Rating score (0 to 1)
            rating, review_count = property_ratings.get(prop.id, (4.0, 0))
            rating_score = max(0.0, min(1.0, (rating - 3.0) / 2.0))

            # 5. User preference score
            pref_score = 0.5
            if user and user.preferred_amenities:
                user_prefs = set(a.lower().strip() for a in user.preferred_amenities)
                overlap = len(user_prefs.intersection(prop_amenities))
                pref_score = min(1.0, 0.4 + (overlap / max(1, len(user_prefs))) * 0.6)

            # 6. Duration suitability
            dur_score = 1.0 if (prop.supported_durations and duration_type in prop.supported_durations) else 0.5

            # Weighted sum
            final_score = (
                settings.WEIGHT_LOCATION * loc_score
                + settings.WEIGHT_PRICE * price_score
                + settings.WEIGHT_AMENITIES * amenity_score
                + settings.WEIGHT_PREFERENCES * pref_score
                + settings.WEIGHT_RATING * rating_score
                + settings.WEIGHT_DURATION * dur_score
            )
            final_score = round(float(final_score), 4)

            # Build explainable feature reasons
            explanations = []
            badges = []

            if dist_km is not None:
                explanations.append(f"Located {dist_km:.1f} km away (straight-line distance), within your {radius_km} km radius.")
                if dist_km <= 3.0:
                    badges.append(f"Nearby ({dist_km:.1f} km)")
            
            if budget is not None:
                if calc_price <= budget:
                    explanations.append(f"Estimated cost ₹{calc_price:.0f} fits within your ₹{budget:.0f} budget.")
                    badges.append("Budget Fit")
                else:
                    explanations.append(f"Estimated cost ₹{calc_price:.0f} is slightly over your ₹{budget:.0f} budget.")
            
            if req_amenities_set and req_amenities_set.issubset(prop_amenities):
                matched_str = ", ".join(sorted(list(req_amenities_set))[:3])
                explanations.append(f"Features all your requested amenities ({matched_str}).")
                badges.append("All Amenities Match")
            
            if rating >= 4.5:
                explanations.append(f"Consistently high guest rating of {rating:.1f}/5.0 ({review_count} reviews).")
                badges.append(f"Top Rated ★ {rating:.1f}")

            if prop.supported_durations and duration_type in prop.supported_durations:
                explanations.append(f"Directly supports {duration_type.replace('_', ' ')} short rental.")

            component_scores = {
                "location_score": round(loc_score, 3),
                "price_score": round(price_score, 3),
                "amenity_score": round(amenity_score, 3),
                "preference_score": round(pref_score, 3),
                "rating_score": round(rating_score, 3),
                "duration_score": round(dur_score, 3),
            }

            from backend.app.schemas.all_schemas import PropertyOut
            prop_out = PropertyOut.model_validate(prop)
            prop_out.average_rating = rating
            prop_out.review_count = review_count

            results.append(
                RecommendationItem(
                    property=prop_out,
                    score=final_score,
                    component_scores=component_scores,
                    straight_line_distance_km=dist_km,
                    calculated_price=calc_price,
                    explanations=explanations,
                    match_badges=badges,
                )
            )

        # Sort descending by final score
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def score_and_rank_ml(
        self,
        candidates: List[Tuple[Property, Optional[float], Dict[str, float]]],
        user: Optional[User],
        user_lat: Optional[float],
        user_lon: Optional[float],
        radius_km: float,
        budget: Optional[float],
        duration_type: str,
        required_amenities: List[str],
        property_ratings: Dict[int, Tuple[float, int]],
        artifact_path: str,
    ) -> List[RecommendationItem]:
        """
        Stage 4: Score using trained Machine Learning ranker model.
        Falls back to baseline if model cannot be loaded.
        """
        model = self._load_ml_model(artifact_path)
        if model is None:
            # Graceful fallback to baseline
            return self.score_and_rank_baseline(
                candidates=candidates,
                user=user,
                user_lat=user_lat,
                user_lon=user_lon,
                radius_km=radius_km,
                budget=budget,
                duration_type=duration_type,
                required_amenities=required_amenities,
                property_ratings=property_ratings,
            )

        baseline_items = self.score_and_rank_baseline(
            candidates=candidates,
            user=user,
            user_lat=user_lat,
            user_lon=user_lon,
            radius_km=radius_km,
            budget=budget,
            duration_type=duration_type,
            required_amenities=required_amenities,
            property_ratings=property_ratings,
        )

        req_amenities_set = set(a.lower().strip() for a in required_amenities) if required_amenities else set()

        # Build feature matrix for ML inference
        features = []
        for item in baseline_items:
            dist = item.straight_line_distance_km or 10.0
            price = item.calculated_price
            bud = budget or (price * 1.2)
            price_ratio = min(3.0, price / max(1.0, bud))
            amenity_ratio = item.component_scores.get("amenity_score", 0.5)
            rating = item.property.average_rating
            review_count = item.property.review_count

            # Feature vector aligns with training pipeline
            feat_row = [dist, price, bud, price_ratio, amenity_ratio, rating, review_count]
            features.append(feat_row)

        if len(features) > 0:
            X = np.array(features)
            try:
                # Predict probability of relevance (class 1, 2, or 3)
                if hasattr(model, "predict_proba"):
                    proba = model.predict_proba(X)
                    # Use probability of positive interaction
                    if proba.shape[1] >= 2:
                        ml_scores = proba[:, -1]
                    else:
                        ml_scores = proba[:, 0]
                else:
                    ml_scores = model.predict(X)

                for idx, item in enumerate(baseline_items):
                    ml_score = float(ml_scores[idx])
                    # Blend 50% ML ranker score with 50% baseline score for explainable stability
                    blended = round(0.5 * ml_score + 0.5 * item.score, 4)
                    item.score = blended
                    item.component_scores["ml_ranker_probability"] = round(ml_score, 4)
                    item.match_badges.append("AI Recommended")

                baseline_items.sort(key=lambda x: x.score, reverse=True)
            except Exception as e:
                print(f"[WARN] ML ranker inference failed, using baseline: {e}")

        return baseline_items

recommender_service = RecommenderService()
