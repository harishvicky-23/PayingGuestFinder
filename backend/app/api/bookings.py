from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.entities import Booking, BookingStatus, Property, User, UserRole
from backend.app.schemas.all_schemas import BookingCreate, BookingStatusUpdate, BookingOut
from backend.app.repositories.booking_repo import BookingRepository
from backend.app.repositories.property_repo import PropertyRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.api.deps import get_current_user, get_current_host_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])

def _enrich_booking_out(db: Session, b: Booking) -> BookingOut:
    prop = PropertyRepository.get_by_id(db, b.property_id)
    renter = UserRepository.get_by_id(db, b.renter_id)
    
    b_out = BookingOut.model_validate(b)
    if prop:
        b_out.property_title = prop.title
        b_out.property_neighbourhood = prop.neighbourhood
        b_out.property_image = prop.images[0] if (prop.images and len(prop.images) > 0) else None
        if b.status == BookingStatus.CONFIRMED.value:
            b_out.exact_address = prop.exact_address
    if renter:
        b_out.renter_name = renter.name
    return b_out

@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Request a new booking. The booking starts in PENDING status until confirmed by host."""
    prop = PropertyRepository.get_by_id(db, booking_in.property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found.")

    if prop.host_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot book your own property.")

    try:
        booking = BookingRepository.create_booking(
            db=db,
            renter_id=current_user.id,
            prop=prop,
            start_datetime=booking_in.start_datetime,
            end_datetime=booking_in.end_datetime,
            duration_type=booking_in.duration_type,
            guest_count=booking_in.guest_count,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return _enrich_booking_out(db, booking)

@router.get("/mine", response_model=List[BookingOut])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all bookings placed by the authenticated renter."""
    bookings = BookingRepository.list_by_renter(db, current_user.id)
    return [_enrich_booking_out(db, b) for b in bookings]

@router.get("/host/requests", response_model=List[BookingOut])
def get_host_bookings(
    current_user: User = Depends(get_current_host_user),
    db: Session = Depends(get_db),
):
    """Retrieve all incoming booking requests for the host's listings."""
    bookings = BookingRepository.list_by_host(db, current_user.id)
    return [_enrich_booking_out(db, b) for b in bookings]

@router.patch("/{id}/status", response_model=BookingOut)
def update_booking_status(
    id: int,
    status_in: BookingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update booking status:
    - Hosts can CONFIRM or REJECT pending bookings.
    - Renters can CANCEL their pending or confirmed bookings.
    - Admins can manage any status.
    """
    booking = BookingRepository.get_by_id(db, id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

    prop = PropertyRepository.get_by_id(db, booking.property_id)
    is_host = (prop and prop.host_id == current_user.id)
    is_renter = (booking.renter_id == current_user.id)
    is_admin = (current_user.role == UserRole.ADMIN.value)

    if not (is_host or is_renter or is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this booking.")

    new_status = status_in.status.upper()

    if new_status in [BookingStatus.CONFIRMED.value, BookingStatus.REJECTED.value] and not (is_host or is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the host can confirm or reject bookings.")

    if new_status == BookingStatus.CANCELLED.value and not (is_renter or is_host or is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to cancel booking.")

    try:
        updated = BookingRepository.update_status(db, booking, new_status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return _enrich_booking_out(db, updated)
