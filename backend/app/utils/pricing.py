from datetime import datetime
from typing import Tuple, Dict, Any

def calculate_duration_hours(start_datetime: datetime, end_datetime: datetime) -> float:
    """Calculate the total duration between start and end datetime in hours."""
    if end_datetime <= start_datetime:
        raise ValueError("End datetime must be strictly after start datetime.")
    delta = end_datetime - start_datetime
    return delta.total_seconds() / 3600.0

def calculate_rental_price(
    duration_type: str,
    duration_hours: float,
    price_per_hour: float,
    price_per_half_day: float,
    price_per_day: float,
) -> Dict[str, float]:
    """
    Compute base price, fee, and total price based on duration type and listing rates.
    Pricing is strictly validated and computed on the backend.
    """
    if duration_type == "hourly":
        hours = max(1.0, duration_hours)
        base_price = round(hours * price_per_hour, 2)
    elif duration_type == "half_day":
        # 1 half-day block (up to ~6 hours)
        blocks = max(1.0, round(duration_hours / 6.0, 1))
        base_price = round(blocks * price_per_half_day, 2)
    elif duration_type == "full_day":
        # 1 full day block (up to 24 hours)
        days = max(1.0, round(duration_hours / 24.0, 1))
        base_price = round(days * price_per_day, 2)
    elif duration_type == "multi_day":
        days = max(1.0, duration_hours / 24.0)
        base_price = round(days * price_per_day * 0.95, 2)  # 5% multi-day discount
    else:
        # Default fallback to hourly
        base_price = round(duration_hours * price_per_hour, 2)

    # 5% marketplace service fee
    fees = round(base_price * 0.05, 2)
    total_price = round(base_price + fees, 2)

    return {
        "base_price": base_price,
        "fees": fees,
        "total_price": total_price,
        "duration_hours": round(duration_hours, 1),
    }
