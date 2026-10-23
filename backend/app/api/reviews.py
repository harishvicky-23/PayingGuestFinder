from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.entities import Review, Favourite, Property, User
from backend.app.schemas.all_schemas import ReviewCreate, ReviewOut, PropertyOut
from backend.app.repositories.review_repo import ReviewRepository
from backend.app.repositories.booking_repo import BookingRepository
from backend.app.repositories.property_repo import PropertyRepository
from backend.app.repositories.favourite_repo import FavouriteRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.api.deps import get_current_user

router = APIRouter(tags=["Reviews and Favourites"])

@router.post("/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a rating and review for a confirmed or completed booking."""
    booking = BookingRepository.get_by_id(db, review_in.booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking reference not found.")

    try:
        review = ReviewRepository.create(
            db=db,
            booking=booking,
            renter_id=current_user.id,
            rating=review_in.rating,
            review_text=review_in.review_text,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    r_out = ReviewOut.model_validate(review)
    r_out.renter_name = current_user.name
    return r_out

@router.get("/properties/{property_id}/reviews", response_model=List[ReviewOut])
def get_property_reviews(property_id: int, db: Session = Depends(get_db)):
    """Retrieve all public reviews and ratings for a property."""
    reviews = ReviewRepository.list_by_property(db, property_id)
    results = []
    for r in reviews:
        renter = UserRepository.get_by_id(db, r.renter_id)
        r_out = ReviewOut.model_validate(r)
        r_out.renter_name = renter.name if renter else "Verified Renter"
        results.append(r_out)
    return results

@router.post("/favourites/{property_id}", status_code=status.HTTP_201_CREATED)
def add_favourite(
    property_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a listing to saved favourites."""
    prop = PropertyRepository.get_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found.")

    FavouriteRepository.add(db, current_user.id, property_id)
    return {"message": "Property added to favourites.", "property_id": property_id}

@router.delete("/favourites/{property_id}", status_code=status.HTTP_200_OK)
def remove_favourite(
    property_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a listing from saved favourites."""
    removed = FavouriteRepository.remove(db, current_user.id, property_id)
    return {"message": "Property removed from favourites.", "removed": removed}

@router.get("/favourites", response_model=List[PropertyOut])
def get_my_favourites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all properties saved in the user's favourites list."""
    favs = FavouriteRepository.list_by_user(db, current_user.id)
    results = []
    for f in favs:
        prop = PropertyRepository.get_by_id(db, f.property_id)
        if prop and prop.active:
            stats = PropertyRepository.get_property_rating_stats(db, prop.id)
            p_out = PropertyOut.model_validate(prop)
            p_out.average_rating = stats["average_rating"]
            p_out.review_count = stats["review_count"]
            results.append(p_out)
    return results
