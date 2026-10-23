from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from backend.app.models.entities import Property, Review, User
from backend.app.schemas.all_schemas import PropertyCreate, PropertyUpdate

class PropertyRepository:
    @staticmethod
    def get_by_id(db: Session, property_id: int) -> Optional[Property]:
        return db.query(Property).filter(Property.id == property_id).first()

    @staticmethod
    def list_properties(
        db: Session,
        active_only: bool = True,
        neighbourhood: Optional[str] = None,
        property_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_guests: Optional[int] = None,
        required_amenities: Optional[List[str]] = None,
        host_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Property]:
        query = db.query(Property)
        if active_only:
            query = query.filter(Property.active == True)
        if host_id is not None:
            query = query.filter(Property.host_id == host_id)
        if neighbourhood:
            query = query.filter(Property.neighbourhood.ilike(f"%{neighbourhood.strip()}%"))
        if property_type and property_type != "all":
            query = query.filter(Property.property_type == property_type)
        if min_guests:
            query = query.filter(Property.maximum_guests >= min_guests)
        if min_price is not None:
            query = query.filter(Property.price_per_hour >= min_price)
        if max_price is not None:
            query = query.filter(Property.price_per_hour <= max_price)

        properties = query.offset(skip).limit(limit).all()

        if required_amenities:
            # Filter in Python for JSON array checking
            req_set = set(a.lower() for a in required_amenities)
            properties = [
                p for p in properties
                if req_set.issubset(set(a.lower() for a in (p.amenities or [])))
            ]

        return properties

    @staticmethod
    def get_property_rating_stats(db: Session, property_id: int) -> Dict[str, Any]:
        result = db.query(
            func.coalesce(func.avg(Review.rating), 0.0),
            func.count(Review.id)
        ).filter(Review.property_id == property_id).first()
        
        avg_rating = round(float(result[0]), 1) if result else 0.0
        review_count = int(result[1]) if result else 0
        return {"average_rating": avg_rating, "review_count": review_count}

    @staticmethod
    def create(db: Session, property_in: PropertyCreate, host_id: int) -> Property:
        prop = Property(
            host_id=host_id,
            title=property_in.title,
            description=property_in.description,
            property_type=property_in.property_type,
            neighbourhood=property_in.neighbourhood,
            latitude=property_in.latitude,
            longitude=property_in.longitude,
            public_location_description=property_in.public_location_description,
            exact_address=property_in.exact_address,
            price_per_hour=property_in.price_per_hour,
            price_per_half_day=property_in.price_per_half_day,
            price_per_day=property_in.price_per_day,
            maximum_guests=property_in.maximum_guests,
            amenities=property_in.amenities,
            supported_durations=property_in.supported_durations,
            house_rules=property_in.house_rules,
            images=property_in.images,
            active=property_in.active,
        )
        db.add(prop)
        db.commit()
        db.refresh(prop)
        return prop

    @staticmethod
    def update(db: Session, prop: Property, property_in: PropertyUpdate) -> Property:
        update_data = property_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prop, field, value)
        db.commit()
        db.refresh(prop)
        return prop

    @staticmethod
    def delete(db: Session, prop: Property) -> None:
        db.delete(prop)
        db.commit()
