from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.models.entities import Property, Booking, BookingStatus, User
from backend.app.schemas.all_schemas import DemandAnalyticsResponse, HostAnalyticsResponse
from backend.app.ml.demand_predictor import demand_predictor_service
from backend.app.api.deps import get_current_host_user

router = APIRouter(prefix="/analytics", tags=["Demand Analytics"])

@router.get("/demand", response_model=DemandAnalyticsResponse)
def get_neighbourhood_demand(
    neighbourhood: Optional[str] = Query(None, description="Chennai neighbourhood name e.g. Guindy, Velachery"),
    target_date: Optional[str] = Query(None, description="Forecast date YYYY-MM-DD"),
):
    """Retrieve forward-looking neighbourhood booking demand predictions."""
    return demand_predictor_service.predict_demand(
        neighbourhood=neighbourhood,
        target_date=target_date,
    )

@router.get("/host", response_model=HostAnalyticsResponse)
def get_host_analytics(
    current_user: User = Depends(get_current_host_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve real-time metrics for the host dashboard:
    Total listings, revenue, bookings, pending requests, and predicted demand in their neighbourhoods.
    """
    props = db.query(Property).filter(Property.host_id == current_user.id).all()
    prop_ids = [p.id for p in props]

    total_listings = len(props)
    
    # Bookings query
    bookings = db.query(Booking).filter(Booking.property_id.isin(prop_ids)).all() if prop_ids else []
    
    confirmed_bookings = [b for b in bookings if b.status == BookingStatus.CONFIRMED.value]
    pending_bookings = [b for b in bookings if b.status == BookingStatus.PENDING.value]
    
    total_revenue = sum(b.total_price for b in confirmed_bookings)
    
    # Occupancy rate calculation (ratio of confirmed bookings to active listings over past period)
    occupancy_rate = round(min(1.0, len(confirmed_bookings) / max(1, total_listings * 4)), 2)

    # Fetch demand forecast for primary neighbourhood
    primary_neighbourhood = props[0].neighbourhood if props else "Guindy"
    demand_resp = demand_predictor_service.predict_demand(neighbourhood=primary_neighbourhood)

    return HostAnalyticsResponse(
        total_listings=total_listings,
        total_bookings=len(confirmed_bookings),
        total_revenue=round(total_revenue, 2),
        occupancy_rate=occupancy_rate,
        pending_requests_count=len(pending_bookings),
        neighbourhood_demand_summary=demand_resp.forecasts,
    )
