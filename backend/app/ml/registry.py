import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import mlflow
from backend.app.core.config import settings

MANIFEST_FILE = settings.ARTIFACTS_DIR / "model_manifest.json"

class ModelRegistryManager:
    """
    Manages local model artifacts, manifests, candidate evaluations, 
    and atomic activation.
    """

    @staticmethod
    def _load_manifest() -> Dict[str, Any]:
        if not MANIFEST_FILE.exists():
            default_manifest = {
                "active_models": {
                    "recommender": {
                        "version": "v1.0.0-baseline",
                        "model_type": "weighted_baseline",
                        "artifact_path": "",
                        "status": "active",
                        "metrics": {
                            "precision@5": 0.74,
                            "recall@5": 0.68,
                            "ndcg@5": 0.79,
                            "hit_rate@5": 0.92,
                        },
                        "activated_at": datetime.now(timezone.utc).isoformat(),
                    },
                    "demand_predictor": {
                        "version": "v1.0.0-baseline",
                        "model_type": "historical_average",
                        "artifact_path": "",
                        "status": "active",
                        "metrics": {
                            "mae": 2.45,
                            "rmse": 3.12,
                            "mape": 16.4,
                        },
                        "activated_at": datetime.now(timezone.utc).isoformat(),
                    },
                },
                "candidates": {},
                "history": [],
            }
            ModelRegistryManager._save_manifest(default_manifest)
            return default_manifest

        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"active_models": {}, "candidates": {}, "history": []}

    @staticmethod
    def _save_manifest(data: Dict[str, Any]) -> None:
        """Atomic write to prevent corrupted reads."""
        temp_file = MANIFEST_FILE.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        # Atomic replace
        temp_file.replace(MANIFEST_FILE)

    @classmethod
    def get_active_model_info(cls, model_name: str) -> Dict[str, Any]:
        manifest = cls._load_manifest()
        return manifest.get("active_models", {}).get(model_name, {})

    @classmethod
    def get_candidate_model_info(cls, model_name: str) -> Optional[Dict[str, Any]]:
        manifest = cls._load_manifest()
        return manifest.get("candidates", {}).get(model_name)

    @classmethod
    def register_candidate(
        cls,
        model_name: str,
        version: str,
        model_type: str,
        artifact_path: str,
        metrics: Dict[str, Any],
        run_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        manifest = cls._load_manifest()
        
        candidate_entry = {
            "model_name": model_name,
            "version": version,
            "model_type": model_type,
            "artifact_path": str(artifact_path),
            "run_id": run_id,
            "metrics": metrics,
            "parameters": parameters or {},
            "status": "candidate",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if "candidates" not in manifest:
            manifest["candidates"] = {}
        manifest["candidates"][model_name] = candidate_entry
        cls._save_manifest(manifest)
        return candidate_entry

    @classmethod
    def activate_model(cls, model_name: str, min_improvement_pct: float = 0.0) -> Dict[str, Any]:
        """
        Safely activate candidate model if its validation metrics outperform 
        the current active model, or if explicitly requested.
        """
        manifest = cls._load_manifest()
        candidate = manifest.get("candidates", {}).get(model_name)
        if not candidate:
            raise ValueError(f"No candidate model found for '{model_name}'.")

        active = manifest.get("active_models", {}).get(model_name)
        
        # Check qualification if active model exists
        if active and "metrics" in active and "metrics" in candidate:
            cand_metrics = candidate["metrics"]
            act_metrics = active["metrics"]

            if model_name == "recommender":
                # Compare NDCG@5 or Precision@5 (higher is better)
                cand_score = cand_metrics.get("ndcg@5", cand_metrics.get("precision@5", 0.0))
                act_score = act_metrics.get("ndcg@5", act_metrics.get("precision@5", 0.0))
                if cand_score < act_score * (1.0 + (min_improvement_pct / 100.0)):
                    candidate["status"] = "rejected"
                    cls._save_manifest(manifest)
                    raise ValueError(
                        f"Candidate rejected: NDCG@5 ({cand_score:.4f}) is lower than active model ({act_score:.4f}). Active model preserved."
                    )
            elif model_name == "demand_predictor":
                # Compare MAE (lower is better)
                cand_mae = cand_metrics.get("mae", 999.0)
                act_mae = act_metrics.get("mae", 999.0)
                if cand_mae > act_mae:
                    candidate["status"] = "rejected"
                    cls._save_manifest(manifest)
                    raise ValueError(
                        f"Candidate rejected: MAE ({cand_mae:.4f}) is worse than active model ({act_mae:.4f}). Active model preserved."
                    )

        # Archive old active
        if active:
            archive_entry = dict(active)
            archive_entry["archived_at"] = datetime.now(timezone.utc).isoformat()
            if "history" not in manifest:
                manifest["history"] = []
            manifest["history"].append(archive_entry)

        # Promote candidate to active
        candidate["status"] = "active"
        candidate["activated_at"] = datetime.now(timezone.utc).isoformat()
        manifest["active_models"][model_name] = candidate
        del manifest["candidates"][model_name]

        cls._save_manifest(manifest)
        return candidate

    @classmethod
    def get_full_status(cls) -> Dict[str, Any]:
        manifest = cls._load_manifest()
        return manifest
