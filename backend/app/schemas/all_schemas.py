from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ================= USER SCHEMAS =================
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    role: str = Field(default="renter", pattern="^(renter|host|admin)$")
    preferred_budget: Optional[float] = None
    preferred_amenities: List[str] = Field(default_factory=list)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    preferred_budget: Optional[float] = None
    preferred_amenities: Optional[List[str]] = None

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None


# ================= PROPERTY SCHEMAS =================
class PropertyBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str
    property_type: str  # workspace, room, studio, apartment, day_cabin
    neighbourhood: str
    latitude: float
    longitude: float
    public_location_description: str
    price_per_hour: float = Field(..., ge=0)
    price_per_half_day: float = Field(..., ge=0)
    price_per_day: float = Field(..., ge=0)
    maximum_guests: int = Field(default=1, ge=1)
    amenities: List[str] = Field(default_factory=list)
    supported_durations: List[str] = Field(default_factory=lambda: ["hourly", "half_day", "full_day"])
    house_rules: str = ""
    images: List[str] = Field(default_factory=list)
    active: bool = True

class PropertyCreate(PropertyBase):
    exact_address: str = Field(..., min_length=5)

class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[str] = None
    neighbourhood: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    public_location_description: Optional[str] = None
    exact_address: Optional[str] = None
    price_per_hour: Optional[float] = None
    price_per_half_day: Optional[float] = None
    price_per_day: Optional[float] = None
    maximum_guests: Optional[int] = None
    amenities: Optional[List[str]] = None
    supported_durations: Optional[List[str]] = None
    house_rules: Optional[str] = None
    images: Optional[List[str]] = None
    active: Optional[bool] = None

class PropertyOut(PropertyBase):
    id: int
    host_id: int
    average_rating: float = 0.0
    review_count: int = 0
    created_at: datetime
    # Note: exact_address is intentionally omitted for public safety

    class Config:
        from_attributes = True

class PropertyDetailOut(PropertyOut):
    exact_address: Optional[str] = None  # Populated only if renter has confirmed booking or user is host
    host_name: Optional[str] = None
    host_email: Optional[str] = None


# ================= BOOKING SCHEMAS =================
class BookingCreate(BaseModel):
    property_id: int
    start_datetime: datetime
    end_datetime: datetime
    duration_type: str = Field(..., pattern="^(hourly|half_day|full_day|multi_day)$")
    guest_count: int = Field(default=1, ge=1)

class BookingStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(CONFIRMED|REJECTED|CANCELLED|COMPLETED)$")

class BookingOut(BaseModel):
    id: int
    renter_id: int
    property_id: int
    start_datetime: datetime
    end_datetime: datetime
    duration_type: str
    guest_count: int
    base_price: float
    fees: float
    total_price: float
    status: str
    payment_status: str
    created_at: datetime
    property_title: Optional[str] = None
    property_neighbourhood: Optional[str] = None
    property_image: Optional[str] = None
    exact_address: Optional[str] = None  # Revealed when CONFIRMED
    renter_name: Optional[str] = None

    class Config:
        from_attributes = True


# ================= REVIEW SCHEMAS =================
class ReviewCreate(BaseModel):
    booking_id: int
    rating: float = Field(..., ge=1.0, le=5.0)
    review_text: str = Field(..., min_length=3, max_length=2000)

class ReviewOut(BaseModel):
    id: int
    booking_id: int
    renter_id: int
    property_id: int
    rating: float
    review_text: str
    created_at: datetime
    renter_name: Optional[str] = None

    class Config:
        from_attributes = True


# ================= RECOMMENDATION SCHEMAS =================
class RecommendationRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_query: Optional[str] = None
    start_datetime: Optional[datetime] = None
    duration_type: str = Field(default="hourly", pattern="^(hourly|half_day|full_day|multi_day)$")
    budget: Optional[float] = None
    guest_count: int = Field(default=1, ge=1)
    required_amenities: List[str] = Field(default_factory=list)
    property_type: Optional[str] = None
    radius_km: float = Field(default=15.0, ge=1.0, le=100.0)
    model_choice: str = Field(default="auto")  # auto, baseline, candidate

class RecommendationItem(BaseModel):
    property: PropertyOut
    score: float
    component_scores: Dict[str, float]
    straight_line_distance_km: Optional[float] = None
    calculated_price: float
    explanations: List[str]
    match_badges: List[str]

class RecommendationResponse(BaseModel):
    session_id: str
    model_version: str
    model_type: str
    count: int
    results: List[RecommendationItem]
    relaxed_filter_suggestions: Optional[List[str]] = None

class RecommendationFeedbackCreate(BaseModel):
    session_id: str
    property_id: int
    feedback_type: str = Field(..., pattern="^(relevant|not_relevant|too_expensive|too_far|missing_amenities)$")
    model_version: str

class RecommendationFeedbackOut(BaseModel):
    id: int
    property_id: int
    session_id: str
    feedback_type: str
    model_version: str
    created_at: datetime

    class Config:
        from_attributes = True


# ================= DEMAND ANALYTICS SCHEMAS =================
class NeighbourhoodDemandItem(BaseModel):
    neighbourhood: str
    target_date: str
    time_slot: str  # morning, afternoon, evening, night
    predicted_demand_score: float  # Expected relative booking volume (0 to 100)
    predicted_booking_requests: float
    historical_avg_requests: float
    confidence_interval_low: float
    confidence_interval_high: float
    demand_level: str  # Low, Moderate, High, Very High

class DemandAnalyticsResponse(BaseModel):
    forecasts: List[NeighbourhoodDemandItem]
    model_version: str
    mae: float
    rmse: float
    data_freshness: str
    data_source_note: str  # Clearly noting synthetic demonstration data vs production data

class HostAnalyticsResponse(BaseModel):
    total_listings: int
    total_bookings: int
    total_revenue: float
    occupancy_rate: float
    pending_requests_count: int
    neighbourhood_demand_summary: List[NeighbourhoodDemandItem]


# ================= MLOPS SCHEMAS =================
class ModelRegistryOut(BaseModel):
    id: int
    model_name: str
    version: str
    model_type: str
    artifact_path: str
    run_id: Optional[str]
    metrics: Dict[str, Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DriftReportOut(BaseModel):
    feature_drifts: Dict[str, Dict[str, Any]]
    overall_drift_detected: bool
    psi_scores: Dict[str, float]
    recommendation_feedback_drift: Dict[str, Any]
    reference_data_size: int
    current_data_size: int
    timestamp: datetime
    alert_message: Optional[str] = None

class RetrainRequest(BaseModel):
    model_name: str = Field(..., pattern="^(recommender|demand_predictor)$")
    evaluate_against_active: bool = True
    auto_activate_if_superior: bool = False
