from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.entities import Property, User, Booking, BookingStatus, UserRole
from backend.app.schemas.all_schemas import PropertyCreate, PropertyUpdate, PropertyOut, PropertyDetailOut
from backend.app.repositories.property_repo import PropertyRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.api.deps import get_current_user, get_current_host_user, get_optional_user

router = APIRouter(prefix="/properties", tags=["Properties"])

@router.get("", response_model=List[PropertyOut])
def list_properties(
    neighbourhood: Optional[str] = Query(None, description="Search by neighbourhood name"),
    property_type: Optional[str] = Query(None, description="workspace_studio, private_room, guest_suite, entire_apartment, day_cabin"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_guests: Optional[int] = Query(None, ge=1),
    amenities: Optional[str] = Query(None, description="Comma-separated amenities e.g. wifi,parking"),
    host_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Retrieve listings with filtering support for discovery."""
    amenities_list = [a.strip() for a in amenities.split(",")] if amenities else None
    props = PropertyRepository.list_properties(
        db=db,
        active_only=True if host_id is None else False,
        neighbourhood=neighbourhood,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        min_guests=min_guests,
        required_amenities=amenities_list,
        host_id=host_id,
        skip=skip,
        limit=limit,
    )

    results = []
    for p in props:
        stats = PropertyRepository.get_property_rating_stats(db, p.id)
        p_out = PropertyOut.model_validate(p)
        p_out.average_rating = stats["average_rating"]
        p_out.review_count = stats["review_count"]
        results.append(p_out)

    return results

@router.get("/{id}", response_model=PropertyDetailOut)
def get_property(
    id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Retrieve property details.
    Exact residential address is kept confidential unless the caller is the host or has a confirmed booking.
    """
    prop = PropertyRepository.get_by_id(db, id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found.")

    stats = PropertyRepository.get_property_rating_stats(db, prop.id)
    host = UserRepository.get_by_id(db, prop.host_id)

    detail = PropertyDetailOut.model_validate(prop)
    detail.average_rating = stats["average_rating"]
    detail.review_count = stats["review_count"]
    detail.host_name = host.name if host else "Host"
    detail.host_email = host.email if (current_user and current_user.role == UserRole.ADMIN.value) else None

    # Reveal exact address if caller is host or renter with confirmed booking
    can_view_address = False
    if current_user:
        if current_user.id == prop.host_id or current_user.role == UserRole.ADMIN.value:
            can_view_address = True
        else:
            confirmed_booking = db.query(Booking).filter(
                Booking.property_id == prop.id,
                Booking.renter_id == current_user.id,
                Booking.status == BookingStatus.CONFIRMED.value,
            ).first()
            if confirmed_booking:
                can_view_address = True

    if can_view_address:
        detail.exact_address = prop.exact_address
    else:
        detail.exact_address = None

    return detail

@router.post("", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
def create_property(
    prop_in: PropertyCreate,
    current_user: User = Depends(get_current_host_user),
    db: Session = Depends(get_db),
):
    """Create a new property listing (Host or Admin only)."""
    prop = PropertyRepository.create(db, prop_in, host_id=current_user.id)
    p_out = PropertyOut.model_validate(prop)
    p_out.average_rating = 0.0
    p_out.review_count = 0
    return p_out

@router.patch("/{id}", response_model=PropertyOut)
def update_property(
    id: int,
    prop_in: PropertyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a property. Hosts can only modify their own properties."""
    prop = PropertyRepository.get_by_id(db, id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found.")

    if prop.host_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to modify this property.")

    updated = PropertyRepository.update(db, prop, prop_in)
    stats = PropertyRepository.get_property_rating_stats(db, updated.id)
    p_out = PropertyOut.model_validate(updated)
    p_out.average_rating = stats["average_rating"]
    p_out.review_count = stats["review_count"]
    return p_out

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a property listing. Hosts can only delete their own listings."""
    prop = PropertyRepository.get_by_id(db, id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found.")

    if prop.host_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this property.")

    PropertyRepository.delete(db, prop)
    return None
