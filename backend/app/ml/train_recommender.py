import os
import sys
import json
import joblib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
import mlflow

from backend.app.core.config import settings
from backend.app.ml.synthetic_generator import generate_synthetic_recommender_dataset
from backend.app.ml.data_validation import validate_recommender_training_data, ValidationError
from backend.app.ml.metrics import (
    calculate_precision_at_k, calculate_recall_at_k, 
    calculate_ndcg_at_k, calculate_hit_rate_at_k
)
from backend.app.ml.registry import ModelRegistryManager

def train_recommender(
    random_seed: int = 42,
    model_type: str = "gradient_boosting",
    n_estimators: int = 100,
    max_depth: int = 4,
    learning_rate: float = 0.1,
    auto_activate: bool = False,
) -> dict:
    print(f"=== Starting Recommender Training Pipeline ({model_type}) ===")
    
    # 1. Dataset generation & loading
    data_file = settings.DATA_DIR / "synthetic_recommender_data.csv"
    if not data_file.exists():
        print("Generating synthetic recommendation interactions dataset...")
        df = generate_synthetic_recommender_dataset(num_sessions=500, candidates_per_session=15, random_seed=random_seed)
        df.to_csv(data_file, index=False)
    else:
        print(f"Loading dataset from {data_file}...")
        df = pd.read_csv(data_file)

    # 2. Data Validation
    valid, errors = validate_recommender_training_data(df)
    if not valid:
        raise ValidationError(f"Dataset validation failed: {errors}")
    print(f"Data validation passed. Dataset shape: {df.shape}")

    # 3. Session-based Split (Prevent data leakage between candidate ranking items)
    sessions = df["session_id"].unique()
    np.random.seed(random_seed)
    np.random.shuffle(sessions)

    n_sessions = len(sessions)
    train_end = int(0.70 * n_sessions)
    val_end = int(0.85 * n_sessions)

    train_sessions = set(sessions[:train_end])
    val_sessions = set(sessions[train_end:val_end])
    test_sessions = set(sessions[val_end:])

    train_df = df[df["session_id"].isin(train_sessions)]
    val_df = df[df["session_id"].isin(val_sessions)]
    test_df = df[df["session_id"].isin(test_sessions)]

    print(f"Split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

    feature_cols = [
        "distance_km", "price", "budget", "price_ratio", 
        "amenity_match_ratio", "rating", "review_count"
    ]

    X_train = train_df[feature_cols].values
    # Binary relevance classification: label > 0
    y_train = (train_df["relevance_label"] > 0).astype(int).values

    X_val = val_df[feature_cols].values
    y_val = (val_df["relevance_label"] > 0).astype(int).values

    X_test = test_df[feature_cols].values
    y_test_binary = (test_df["relevance_label"] > 0).astype(int).values
    y_test_multilevel = test_df["relevance_label"].values

    # 4. Train Model
    if model_type == "gradient_boosting":
        model = GradientBoostingClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_seed,
        )
    else:
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_seed,
        )

    model.fit(X_train, y_train)

    # 5. Evaluate on Test Set
    test_preds_proba = model.predict_proba(X_test)[:, 1]

    # Baseline scoring on test set: heuristic weighted formula
    baseline_scores = (
        - 0.08 * test_df["distance_km"].values
        - 0.5 * np.maximum(0.0, test_df["price_ratio"].values - 1.0)
        + 1.5 * test_df["amenity_match_ratio"].values
        + 0.4 * (test_df["rating"].values - 3.0)
    )

    k = 5
    ml_ndcg = calculate_ndcg_at_k(y_test_multilevel, test_preds_proba, k=k)
    ml_prec = calculate_precision_at_k(y_test_binary, test_preds_proba, k=k)
    ml_rec = calculate_recall_at_k(y_test_binary, test_preds_proba, k=k)
    ml_hit = calculate_hit_rate_at_k(y_test_binary, test_preds_proba, k=k)

    base_ndcg = calculate_ndcg_at_k(y_test_multilevel, baseline_scores, k=k)
    base_prec = calculate_precision_at_k(y_test_binary, baseline_scores, k=k)
    base_rec = calculate_recall_at_k(y_test_binary, baseline_scores, k=k)
    base_hit = calculate_hit_rate_at_k(y_test_binary, baseline_scores, k=k)

    metrics = {
        "precision@5": round(ml_prec, 4),
        "recall@5": round(ml_rec, 4),
        "ndcg@5": round(ml_ndcg, 4),
        "hit_rate@5": round(ml_hit, 4),
        "baseline_ndcg@5": round(base_ndcg, 4),
        "baseline_precision@5": round(base_prec, 4),
    }

    # Clean metric names for MLflow (replace @ with _at_)
    mlflow_metrics = {k.replace("@", "_at_"): v for k, v in metrics.items()}

    print("Candidate ML Evaluation:", metrics)

    # 6. MLflow Experiment Tracking
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment("StayNearby_Recommender")

    run_id = None
    with mlflow.start_run(run_name=f"{model_type}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
        run_id = run.info.run_id
        mlflow.log_params({
            "model_type": model_type,
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate if model_type == "gradient_boosting" else None,
            "random_seed": random_seed,
            "n_features": len(feature_cols),
            "train_samples": len(train_df),
        })
        mlflow.log_metrics(mlflow_metrics)

    # 7. Save Model Artifact
    version_tag = f"v{datetime.now().strftime('%Y%m%d%H%M')}"
    artifact_name = f"recommender_{model_type}_{version_tag}.joblib"
    artifact_path = settings.ARTIFACTS_DIR / artifact_name
    joblib.dump(model, artifact_path)
    print(f"Saved model artifact to {artifact_path}")

    # 8. Register Candidate in Manifest
    candidate = ModelRegistryManager.register_candidate(
        model_name="recommender",
        version=version_tag,
        model_type=model_type,
        artifact_path=str(artifact_path),
        metrics=metrics,
        run_id=run_id,
        parameters={"n_estimators": n_estimators, "max_depth": max_depth},
    )

    if auto_activate:
        print("Auto-activating candidate model...")
        ModelRegistryManager.activate_model("recommender")
        print("Candidate successfully activated!")

    return candidate

if __name__ == "__main__":
    train_recommender(auto_activate=True)
