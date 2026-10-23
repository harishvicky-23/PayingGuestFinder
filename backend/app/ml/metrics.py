import math
from typing import List, Dict, Any, Sequence
import numpy as np

def calculate_precision_at_k(y_true: Sequence[int], y_scores: Sequence[float], k: int = 5) -> float:
    """
    Precision@K: Proportion of recommended items in the top K that are relevant.
    """
    if len(y_true) == 0 or len(y_scores) == 0 or k <= 0:
        return 0.0
    
    order = np.argsort(y_scores)[::-1][:k]
    top_k_labels = np.array(y_true)[order]
    return float(np.sum(top_k_labels > 0) / float(k))

def calculate_recall_at_k(y_true: Sequence[int], y_scores: Sequence[float], k: int = 5) -> float:
    """
    Recall@K: Proportion of relevant items that are found in the top K.
    """
    total_relevant = np.sum(np.array(y_true) > 0)
    if total_relevant == 0 or k <= 0:
        return 0.0
    
    order = np.argsort(y_scores)[::-1][:k]
    top_k_labels = np.array(y_true)[order]
    return float(np.sum(top_k_labels > 0) / float(total_relevant))

def calculate_ndcg_at_k(y_true: Sequence[int], y_scores: Sequence[float], k: int = 5) -> float:
    """
    Normalized Discounted Cumulative Gain at K (NDCG@K).
    """
    if len(y_true) == 0 or k <= 0:
        return 0.0

    order = np.argsort(y_scores)[::-1][:k]
    actual_top_k = np.array(y_true)[order]

    # DCG
    dcg = 0.0
    for i, rel in enumerate(actual_top_k):
        if rel > 0:
            dcg += (2.0 ** rel - 1.0) / math.log2(i + 2.0)

    # Ideal DCG
    ideal_order = np.argsort(y_true)[::-1][:k]
    ideal_top_k = np.array(y_true)[ideal_order]
    idcg = 0.0
    for i, rel in enumerate(ideal_top_k):
        if rel > 0:
            idcg += (2.0 ** rel - 1.0) / math.log2(i + 2.0)

    if idcg == 0.0:
        return 0.0
    return float(dcg / idcg)

def calculate_hit_rate_at_k(y_true: Sequence[int], y_scores: Sequence[float], k: int = 5) -> float:
    """
    Hit Rate@K: 1.0 if at least one relevant item appears in top K, else 0.0.
    """
    if len(y_true) == 0 or k <= 0:
        return 0.0
    order = np.argsort(y_scores)[::-1][:k]
    top_k_labels = np.array(y_true)[order]
    return 1.0 if np.sum(top_k_labels > 0) > 0 else 0.0

def calculate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Compute MAE, RMSE, and zero-safe MAPE for regression models.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    
    # Zero-safe MAPE (avoid divide by zero)
    mask = y_true > 0
    if np.sum(mask) > 0:
        mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)
    else:
        mape = 0.0
        
    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 2),
    }
