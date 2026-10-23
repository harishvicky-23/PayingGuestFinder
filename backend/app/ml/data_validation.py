from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np

class ValidationError(Exception):
    """Raised when dataset fails validation checks."""
    pass

def validate_recommender_training_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate dataset used for recommender ranking model training.
    """
    errors: List[str] = []
    
    required_cols = [
        "session_id", "property_id", "distance_km", "price", 
        "budget", "rating", "amenity_match_ratio", "relevance_label"
    ]
    
    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Missing required column: '{col}'")

    if errors:
        return False, errors

    # Check non-empty
    if len(df) == 0:
        errors.append("Dataset is empty.")
        return False, errors

    # Check duplicate session-property pairs
    duplicates = df.duplicated(subset=["session_id", "property_id"]).sum()
    if duplicates > 0:
        errors.append(f"Found {duplicates} duplicate (session_id, property_id) entries.")

    # Range checks
    if (df["distance_km"] < 0).any():
        errors.append("Invalid distance: contains negative values.")
    if (df["price"] < 0).any():
        errors.append("Invalid price: contains negative values.")
    if (df["budget"] < 0).any():
        errors.append("Invalid budget: contains negative values.")
    if ((df["rating"] < 0.0) | (df["rating"] > 5.0)).any():
        errors.append("Invalid rating: values must be within [0.0, 5.0].")
    if ((df["amenity_match_ratio"] < 0.0) | (df["amenity_match_ratio"] > 1.0)).any():
        errors.append("Invalid amenity_match_ratio: values must be within [0.0, 1.0].")
    if not set(df["relevance_label"].unique()).issubset({0, 1, 2, 3}):
        errors.append("Relevance label must be integer in {0, 1, 2, 3}.")

    # Null checks
    null_counts = df[required_cols].isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            errors.append(f"Column '{col}' contains {count} missing (NaN) values.")

    return len(errors) == 0, errors

def validate_demand_training_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate dataset used for neighbourhood demand forecasting.
    """
    errors: List[str] = []
    required_cols = [
        "neighbourhood", "date", "day_of_week", "time_slot", 
        "available_listings", "avg_price", "historical_requests", "actual_requests"
    ]

    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Missing required column: '{col}'")

    if errors:
        return False, errors

    if len(df) == 0:
        errors.append("Demand dataset is empty.")
        return False, errors

    if (df["available_listings"] < 0).any():
        errors.append("Negative available_listings found.")
    if (df["avg_price"] < 0).any():
        errors.append("Negative avg_price found.")
    if (df["actual_requests"] < 0).any():
        errors.append("Negative actual_requests found.")

    valid_slots = {"morning", "afternoon", "evening", "night"}
    slot_diff = set(df["time_slot"].unique()) - valid_slots
    if slot_diff:
        errors.append(f"Invalid time slots found: {slot_diff}. Expected {valid_slots}.")

    return len(errors) == 0, errors
