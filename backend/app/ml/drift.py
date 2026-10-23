from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import numpy as np
import pandas as pd

def calculate_psi(reference: np.ndarray, current: np.ndarray, num_buckets: int = 10) -> float:
    """
    Calculate the Population Stability Index (PSI) between a reference and current distribution.
    
    PSI interpretation:
    - PSI < 0.1: No significant distribution change.
    - 0.1 <= PSI < 0.25: Moderate change / slight drift.
    - PSI >= 0.25: Significant change / action required.
    """
    reference = np.asarray(reference, dtype=float)
    current = np.asarray(current, dtype=float)

    if len(reference) == 0 or len(current) == 0:
        return 0.0

    # Handle single unique value or zero variance
    if np.all(reference == reference[0]) and np.all(current == current[0]):
        return 0.0

    # Determine quantile bins based on reference data
    percentiles = np.linspace(0, 100, num_buckets + 1)
    bins = np.percentile(reference, percentiles)
    bins = np.unique(bins)
    
    if len(bins) < 2:
        return 0.0
    
    bins[0] = -np.inf
    bins[-1] = np.inf

    ref_counts, _ = np.histogram(reference, bins=bins)
    cur_counts, _ = np.histogram(current, bins=bins)

    # Add small epsilon to avoid divide by zero or log(0)
    eps = 1e-4
    ref_pct = (ref_counts + eps) / (len(reference) + eps * len(ref_counts))
    cur_pct = (cur_counts + eps) / (len(current) + eps * len(cur_counts))

    psi_value = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))
    return float(round(max(0.0, psi_value), 4))

def assess_feature_drifts(
    reference_df: pd.DataFrame, 
    current_df: pd.DataFrame, 
    features: List[str]
) -> Dict[str, Any]:
    """
    Assess drift across multiple features and generate an overall drift report.
    """
    feature_reports: Dict[str, Dict[str, Any]] = {}
    psi_scores: Dict[str, float] = {}
    drift_detected = False
    alerts: List[str] = []

    for feat in features:
        if feat in reference_df.columns and feat in current_df.columns:
            ref_vals = reference_df[feat].dropna().values
            cur_vals = current_df[feat].dropna().values
            
            if len(ref_vals) >= 10 and len(cur_vals) >= 10:
                psi = calculate_psi(ref_vals, cur_vals)
                psi_scores[feat] = psi
                
                status = "stable"
                if psi >= 0.25:
                    status = "significant_drift"
                    drift_detected = True
                    alerts.append(f"Significant drift detected in feature '{feat}' (PSI: {psi}).")
                elif psi >= 0.10:
                    status = "moderate_drift"
                    alerts.append(f"Moderate shift in feature '{feat}' (PSI: {psi}).")

                feature_reports[feat] = {
                    "psi": psi,
                    "status": status,
                    "ref_mean": float(round(np.mean(ref_vals), 2)),
                    "cur_mean": float(round(np.mean(cur_vals), 2)),
                    "ref_std": float(round(np.std(ref_vals), 2)),
                    "cur_std": float(round(np.std(cur_vals), 2)),
                }

    return {
        "feature_drifts": feature_reports,
        "overall_drift_detected": drift_detected,
        "psi_scores": psi_scores,
        "alerts": alerts,
        "reference_data_size": len(reference_df),
        "current_data_size": len(current_df),
        "timestamp": datetime.now(timezone.utc),
    }
