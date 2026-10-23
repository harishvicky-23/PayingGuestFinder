from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.entities import Review, Booking, BookingStatus

class ReviewRepository:
    @staticmethod
    def get_by_booking_id(db: Session, booking_id: int) -> Optional[Review]:
        return db.query(Review).filter(Review.booking_id == booking_id).first()

    @staticmethod
    def list_by_property(db: Session, property_id: int) -> List[Review]:
        return db.query(Review).filter(Review.property_id == property_id).order_by(Review.created_at.desc()).all()

    @staticmethod
    def create(db: Session, booking: Booking, renter_id: int, rating: float, review_text: str) -> Review:
        if booking.renter_id != renter_id:
            raise ValueError("You can only review your own bookings.")
        
        if booking.status not in [BookingStatus.COMPLETED.value, BookingStatus.CONFIRMED.value]:
            raise ValueError("Reviews can only be submitted for confirmed or completed bookings.")

        existing = ReviewRepository.get_by_booking_id(db, booking.id)
        if existing:
            raise ValueError("This booking has already been reviewed.")

        review = Review(
            booking_id=booking.id,
            renter_id=renter_id,
            property_id=booking.property_id,
            rating=rating,
            review_text=review_text,
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
