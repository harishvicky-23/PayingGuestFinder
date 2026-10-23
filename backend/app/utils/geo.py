import math
from typing import Optional, Tuple, Dict

# Approximate centroid coordinates for prominent Chennai neighbourhoods
# Used for neighbourhood lookup and synthetic demo properties
CHENNAI_NEIGHBOURHOODS: Dict[str, Tuple[float, float]] = {
    "Guindy": (13.0067, 80.2025),
    "Velachery": (12.9756, 80.2206),
    "Adyar": (13.0012, 80.2565),
    "T. Nagar": (13.0418, 80.2341),
    "Anna Nagar": (13.0850, 80.2101),
    "Mylapore": (13.0368, 80.2676),
    "OMR (Thoraipakkam)": (12.9345, 80.2312),
    "Nungambakkam": (13.0569, 80.2425),
    "Besant Nagar": (13.0003, 80.2667),
    "Alwarpet": (13.0335, 80.2505),
}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the straight-line distance between two points on Earth using the Haversine formula.
    
    Returns:
        Distance in kilometers (straight-line distance, not driving distance).
    """
    R = 6371.0  # Earth's radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = R * c
    return round(distance, 2)

def resolve_location_coordinates(
    query: Optional[str] = None, 
    lat: Optional[float] = None, 
    lon: Optional[float] = None
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Resolves coordinates from explicit lat/lon or known neighbourhood query.
    Does NOT invent GPS coordinates.
    """
    if lat is not None and lon is not None:
        return lat, lon, "custom_coordinates"
    
    if query:
        query_norm = query.strip().lower()
        for name, coords in CHENNAI_NEIGHBOURHOODS.items():
            if name.lower() in query_norm or query_norm in name.lower():
                return coords[0], coords[1], name

    return None, None, None
