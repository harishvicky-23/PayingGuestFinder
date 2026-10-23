from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from backend.app.models.entities import Booking, BookingStatus, Property
from backend.app.utils.pricing import calculate_duration_hours, calculate_rental_price

class BookingRepository:
    @staticmethod
    def get_by_id(db: Session, booking_id: int) -> Optional[Booking]:
        return db.query(Booking).filter(Booking.id == booking_id).first()

    @staticmethod
    def list_by_renter(db: Session, renter_id: int) -> List[Booking]:
        return db.query(Booking).filter(Booking.renter_id == renter_id).order_by(Booking.start_datetime.desc()).all()

    @staticmethod
    def list_by_host(db: Session, host_id: int) -> List[Booking]:
        return (
            db.query(Booking)
            .join(Property, Booking.property_id == Property.id)
            .filter(Property.host_id == host_id)
            .order_by(Booking.created_at.desc())
            .all()
        )

    @staticmethod
    def check_conflicting_confirmed_bookings(
        db: Session,
        property_id: int,
        start_dt: datetime,
        end_dt: datetime,
        exclude_booking_id: Optional[int] = None,
    ) -> bool:
        """
        Check if any CONFIRMED booking overlaps with [start_dt, end_dt].
        Returns True if there is a conflict.
        Two intervals [A_start, A_end] and [B_start, B_end] overlap if:
        A_start < B_end AND A_end > B_start
        """
        query = db.query(Booking).filter(
            Booking.property_id == property_id,
            Booking.status == BookingStatus.CONFIRMED.value,
            Booking.start_datetime < end_dt,
            Booking.end_datetime > start_dt,
        )
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)

        conflict = query.first()
        return conflict is not None

    @staticmethod
    def create_booking(
        db: Session,
        renter_id: int,
        prop: Property,
        start_datetime: datetime,
        end_datetime: datetime,
        duration_type: str,
        guest_count: int,
    ) -> Booking:
        # Check active
        if not prop.active:
            raise ValueError("Property is not currently active for bookings.")

        # Check capacity
        if guest_count > prop.maximum_guests:
            raise ValueError(f"Guest count ({guest_count}) exceeds maximum property capacity ({prop.maximum_guests}).")

        # Check supported duration
        if prop.supported_durations and duration_type not in prop.supported_durations:
            raise ValueError(f"Duration type '{duration_type}' is not supported by this property. Supported: {prop.supported_durations}")

        # Check duration hours
        duration_hours = calculate_duration_hours(start_datetime, end_datetime)
        if duration_hours <= 0:
            raise ValueError("End datetime must be after start datetime.")

        # Check conflicting confirmed bookings
        if BookingRepository.check_conflicting_confirmed_bookings(db, prop.id, start_datetime, end_datetime):
            raise ValueError("The requested time interval overlaps with an existing confirmed booking.")

        # Compute price strictly on backend
        price_info = calculate_rental_price(
            duration_type=duration_type,
            duration_hours=duration_hours,
            price_per_hour=prop.price_per_hour,
            price_per_half_day=prop.price_per_half_day,
            price_per_day=prop.price_per_day,
        )

        booking = Booking(
            renter_id=renter_id,
            property_id=prop.id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            duration_type=duration_type,
            guest_count=guest_count,
            base_price=price_info["base_price"],
            fees=price_info["fees"],
            total_price=price_info["total_price"],
            status=BookingStatus.PENDING.value,
            payment_status="SIMULATED_PAID",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def update_status(db: Session, booking: Booking, new_status: str) -> Booking:
        if new_status == BookingStatus.CONFIRMED.value:
            # Check for conflict right before confirming to guarantee zero race condition
            conflict = BookingRepository.check_conflicting_confirmed_bookings(
                db, booking.property_id, booking.start_datetime, booking.end_datetime, exclude_booking_id=booking.id
            )
            if conflict:
                raise ValueError("Cannot confirm booking: conflicting booking has already been confirmed for this time slot.")

        booking.status = new_status
        db.commit()
        db.refresh(booking)
        return booking
