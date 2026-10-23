import enum
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, 
    Text, JSON, UniqueConstraint, Enum as SAEnum, Index
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class UserRole(str, enum.Enum):
    RENTER = "renter"
    HOST = "host"
    ADMIN = "admin"

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class PaymentStatus(str, enum.Enum):
    SIMULATED_PAID = "SIMULATED_PAID"
    UNPAID = "UNPAID"
    REFUNDED = "REFUNDED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.RENTER.value, nullable=False)
    preferred_budget = Column(Float, nullable=True)
    preferred_amenities = Column(JSON, default=list)  # list of strings
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    properties = relationship("Property", back_populates="host", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="renter", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="renter")
    favourites = relationship("Favourite", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("RecommendationFeedback", back_populates="user")


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    property_type = Column(String(100), nullable=False)  # workspace, room, studio, apartment, day_cabin
    neighbourhood = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    public_location_description = Column(String(255), nullable=False)
    exact_address = Column(String(255), nullable=False)  # Protected: only revealed on confirmed booking
    
    price_per_hour = Column(Float, nullable=False)
    price_per_half_day = Column(Float, nullable=False)
    price_per_day = Column(Float, nullable=False)
    maximum_guests = Column(Integer, nullable=False, default=1)
    
    amenities = Column(JSON, default=list, nullable=False)  # e.g. ["wifi", "ac", "workspace", "parking"]
    supported_durations = Column(JSON, default=list, nullable=False)  # e.g. ["hourly", "half_day", "full_day"]
    house_rules = Column(Text, default="", nullable=False)
    images = Column(JSON, default=list, nullable=False)  # list of image URLs
    
    active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    host = relationship("User", back_populates="properties")
    availability_slots = relationship("AvailabilitySlot", back_populates="property", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="property", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="property", cascade="all, delete-orphan")
    favourites = relationship("Favourite", back_populates="property", cascade="all, delete-orphan")
    feedbacks = relationship("RecommendationFeedback", back_populates="property")


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    availability_status = Column(String(50), default="available", nullable=False)  # available, booked, blocked

    property = relationship("Property", back_populates="availability_slots")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    renter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=False, index=True)
    duration_type = Column(String(50), nullable=False)  # hourly, half_day, full_day, multi_day
    guest_count = Column(Integer, nullable=False, default=1)
    
    base_price = Column(Float, nullable=False)
    fees = Column(Float, nullable=False, default=0.0)
    total_price = Column(Float, nullable=False)
    
    status = Column(String(50), default=BookingStatus.PENDING.value, nullable=False, index=True)
    payment_status = Column(String(50), default=PaymentStatus.SIMULATED_PAID.value, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    renter = relationship("User", back_populates="bookings")
    property = relationship("Property", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    renter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)  # 1.0 to 5.0
    review_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    booking = relationship("Booking", back_populates="review")
    renter = relationship("User", back_populates="reviews")
    property = relationship("Property", back_populates="reviews")


class Favourite(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "property_id", name="uq_user_property_favourite"),
    )

    user = relationship("User", back_populates="favourites")
    property = relationship("Property", back_populates="favourites")


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    feedback_type = Column(String(50), nullable=False)  # relevant, not_relevant, too_expensive, too_far, missing_amenities
    model_version = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="feedbacks")
    property = relationship("Property", back_populates="feedbacks")


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, nullable=True)
    model_version = Column(String(50), nullable=False)
    candidate_count = Column(Integer, nullable=False)
    returned_count = Column(Integer, nullable=False)
    search_latitude = Column(Float, nullable=True)
    search_longitude = Column(Float, nullable=True)
    duration_type = Column(String(50), nullable=True)
    budget = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)  # recommender, demand_predictor
    version = Column(String(50), nullable=False)
    model_type = Column(String(100), nullable=False)  # baseline, gradient_boosting, random_forest, hist_gb
    artifact_path = Column(String(500), nullable=False)
    run_id = Column(String(100), nullable=True)
    metrics = Column(JSON, default=dict, nullable=False)
    status = Column(String(50), default="candidate", nullable=False, index=True)  # active, candidate, archived, rejected
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
