import os
import joblib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
import mlflow

from backend.app.core.config import settings
from backend.app.ml.synthetic_generator import generate_synthetic_demand_dataset, CHENNAI_AREAS, TIME_SLOTS
from backend.app.ml.data_validation import validate_demand_training_data, ValidationError
from backend.app.ml.metrics import calculate_regression_metrics
from backend.app.ml.registry import ModelRegistryManager

def train_demand_model(
    random_seed: int = 42,
    model_type: str = "hist_gradient_boosting",
    auto_activate: bool = False,
) -> dict:
    print(f"=== Starting Neighbourhood Demand Forecasting Training Pipeline ({model_type}) ===")

    # 1. Dataset Generation / Loading
    data_file = settings.DATA_DIR / "synthetic_demand_data.csv"
    if not data_file.exists():
        print("Generating synthetic neighbourhood demand time-series dataset...")
        df = generate_synthetic_demand_dataset(start_date="2026-08-01", num_days=90, random_seed=random_seed)
        df.to_csv(data_file, index=False)
    else:
        print(f"Loading dataset from {data_file}...")
        df = pd.read_csv(data_file)

    # 2. Validation
    valid, errors = validate_demand_training_data(df)
    if not valid:
        raise ValidationError(f"Demand data validation failed: {errors}")
    print(f"Data validation passed. Dataset shape: {df.shape}")

    # 3. Categorical Encodings
    area_map = {name: idx for idx, name in enumerate(CHENNAI_AREAS)}
    slot_map = {slot: idx for idx, slot in enumerate(TIME_SLOTS)}
    df["area_code"] = df["neighbourhood"].map(area_map).fillna(0).astype(int)
    df["slot_code"] = df["time_slot"].map(slot_map).fillna(0).astype(int)

    # 4. Time-based Split (Chronological train/test split to prevent temporal data leakage)
    dates = sorted(df["date"].unique())
    split_idx = int(0.80 * len(dates))
    train_dates = set(dates[:split_idx])
    test_dates = set(dates[split_idx:])

    train_df = df[df["date"].isin(train_dates)]
    test_df = df[df["date"].isin(test_dates)]

    print(f"Chronological split: Train dates={len(train_dates)}, Test dates={len(test_dates)}")

    features = [
        "day_of_week", "is_weekend", "month", "area_code", "slot_code",
        "avg_price", "available_listings", "historical_requests"
    ]
    target = "actual_requests"

    X_train = train_df[features].values
    y_train = train_df[target].values
    X_test = test_df[features].values
    y_test = test_df[target].values

    # 5. Train Model
    if model_type == "hist_gradient_boosting":
        model = HistGradientBoostingRegressor(
            max_iter=120,
            max_depth=5,
            learning_rate=0.08,
            random_state=random_seed,
        )
    else:
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=6,
            random_state=random_seed,
        )

    model.fit(X_train, y_train)

    # 6. Evaluation
    y_pred = model.predict(X_test)
    metrics = calculate_regression_metrics(y_test, y_pred)

    # Baseline: historical average predictor
    baseline_pred = test_df["historical_requests"].values
    baseline_metrics = calculate_regression_metrics(y_test, baseline_pred)

    metrics["baseline_mae"] = baseline_metrics["mae"]
    metrics["baseline_rmse"] = baseline_metrics["rmse"]

    print("Candidate Demand Model Metrics:", metrics)

    # 7. MLflow Experiment Logging
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment("StayNearby_Demand_Prediction")

    run_id = None
    with mlflow.start_run(run_name=f"{model_type}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
        run_id = run.info.run_id
        mlflow.log_params({
            "model_type": model_type,
            "random_seed": random_seed,
            "train_samples": len(train_df),
            "test_samples": len(test_df),
            "features": ",".join(features),
        })
        mlflow.log_metrics({
            "mae": metrics["mae"],
            "rmse": metrics["rmse"],
            "mape": metrics["mape"],
            "baseline_mae": metrics["baseline_mae"],
            "baseline_rmse": metrics["baseline_rmse"],
        })

    # 8. Save Artifact & Register Candidate
    version_tag = f"v{datetime.now().strftime('%Y%m%d%H%M')}"
    artifact_name = f"demand_{model_type}_{version_tag}.joblib"
    artifact_path = settings.ARTIFACTS_DIR / artifact_name
    joblib.dump(model, artifact_path)
    print(f"Saved demand model artifact to {artifact_path}")

    candidate = ModelRegistryManager.register_candidate(
        model_name="demand_predictor",
        version=version_tag,
        model_type=model_type,
        artifact_path=str(artifact_path),
        metrics=metrics,
        run_id=run_id,
        parameters={"model_type": model_type},
    )

    if auto_activate:
        print("Auto-activating candidate demand model...")
        ModelRegistryManager.activate_model("demand_predictor")
        print("Candidate successfully activated!")

    return candidate

if __name__ == "__main__":
    train_demand_model(auto_activate=True)
