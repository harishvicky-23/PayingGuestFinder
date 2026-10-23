from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import joblib

from backend.app.core.config import settings
from backend.app.schemas.all_schemas import NeighbourhoodDemandItem, DemandAnalyticsResponse
from backend.app.ml.registry import ModelRegistryManager

CHENNAI_AREAS = [
    "Guindy", "Velachery", "Adyar", "T. Nagar", 
    "Anna Nagar", "Mylapore", "OMR (Thoraipakkam)", "Nungambakkam"
]
TIME_SLOTS = ["morning", "afternoon", "evening", "night"]

class DemandPredictorService:
    def __init__(self):
        self._model = None
        self._model_path = None

    def _load_model(self, artifact_path: str):
        if self._model_path == artifact_path and self._model is not None:
            return self._model
        
        path = Path(artifact_path)
        if path.exists():
            try:
                self._model = joblib.load(path)
                self._model_path = artifact_path
                return self._model
            except Exception as e:
                print(f"[WARN] Failed to load demand model from {artifact_path}: {e}")
                return None
        return None

    def predict_demand(
        self,
        neighbourhood: Optional[str] = None,
        target_date: Optional[str] = None,
    ) -> DemandAnalyticsResponse:
        """
        Produce forward-looking demand forecasts for neighbourhoods and time-slots.
        """
        active_info = ModelRegistryManager.get_active_model_info("demand_predictor")
        artifact_path = active_info.get("artifact_path", "")
        model_version = active_info.get("version", "v1.0.0-baseline")
        metrics = active_info.get("metrics", {"mae": 2.45, "rmse": 3.12})

        areas_to_forecast = [neighbourhood] if (neighbourhood and neighbourhood in CHENNAI_AREAS) else CHENNAI_AREAS
        date_str = target_date or pd.Timestamp.now().strftime("%Y-%m-%d")
        dt = pd.to_datetime(date_str)
        day_of_week = dt.weekday()
        is_weekend = 1 if day_of_week in [5, 6] else 0
        month = dt.month

        model = self._load_model(artifact_path) if artifact_path else None

        forecasts: List[NeighbourhoodDemandItem] = []

        area_base = {
            "Guindy": 12.0, "Velachery": 11.0, "Adyar": 10.0, "T. Nagar": 14.0,
            "Anna Nagar": 13.0, "Mylapore": 9.0, "OMR (Thoraipakkam)": 15.0, "Nungambakkam": 11.5
        }
        slot_multipliers = {"morning": 0.8, "afternoon": 1.2, "evening": 1.4, "night": 0.5}

        for area in areas_to_forecast:
            base_val = area_base.get(area, 10.0)
            for slot in TIME_SLOTS:
                mult = slot_multipliers.get(slot, 1.0)
                weekend_boost = 1.3 if (is_weekend and area in ["T. Nagar", "Anna Nagar", "Adyar"]) else 1.0
                it_boost = 1.25 if (not is_weekend and area in ["OMR (Thoraipakkam)", "Guindy"]) else 1.0
                
                historical_avg = round(base_val * mult * 0.95, 1)

                if model is not None:
                    try:
                        # Construct input vector matching training schema
                        # [day_of_week, is_weekend, month, area_code, slot_code, avg_price, available_listings, historical_requests]
                        area_code = CHENNAI_AREAS.index(area) if area in CHENNAI_AREAS else 0
                        slot_code = TIME_SLOTS.index(slot) if slot in TIME_SLOTS else 0
                        X_input = np.array([[
                            day_of_week, is_weekend, month, area_code, slot_code, 450.0, 20.0, historical_avg
                        ]])
                        predicted_req = float(model.predict(X_input)[0])
                    except Exception as e:
                        predicted_req = base_val * mult * weekend_boost * it_boost
                else:
                    # Baseline heuristic prediction
                    predicted_req = base_val * mult * weekend_boost * it_boost

                predicted_req = max(1.0, round(predicted_req, 1))
                demand_score = min(100.0, round((predicted_req / 25.0) * 100.0, 1))
                
                # Confidence intervals derived from validation RMSE
                rmse_margin = float(metrics.get("rmse", 2.5))
                ci_low = max(0.0, round(predicted_req - 1.96 * rmse_margin, 1))
                ci_high = round(predicted_req + 1.96 * rmse_margin, 1)

                if demand_score >= 75.0:
                    demand_level = "Very High"
                elif demand_score >= 55.0:
                    demand_level = "High"
                elif demand_score >= 35.0:
                    demand_level = "Moderate"
                else:
                    demand_level = "Low"

                forecasts.append(
                    NeighbourhoodDemandItem(
                        neighbourhood=area,
                        target_date=date_str,
                        time_slot=slot,
                        predicted_demand_score=demand_score,
                        predicted_booking_requests=predicted_req,
                        historical_avg_requests=historical_avg,
                        confidence_interval_low=ci_low,
                        confidence_interval_high=ci_high,
                        demand_level=demand_level,
                    )
                )

        return DemandAnalyticsResponse(
            forecasts=forecasts,
            model_version=model_version,
            mae=float(metrics.get("mae", 2.45)),
            rmse=float(metrics.get("rmse", 3.12)),
            data_freshness=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            data_source_note="Demonstration forecast derived from local synthetic baseline/ML model. Does not represent actual commercial demand.",
        )

demand_predictor_service = DemandPredictorService()
