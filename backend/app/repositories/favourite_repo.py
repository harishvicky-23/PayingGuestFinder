from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.entities import Favourite

class FavouriteRepository:
    @staticmethod
    def list_by_user(db: Session, user_id: int) -> List[Favourite]:
        return db.query(Favourite).filter(Favourite.user_id == user_id).order_by(Favourite.created_at.desc()).all()

    @staticmethod
    def is_favourite(db: Session, user_id: int, property_id: int) -> bool:
        return db.query(Favourite).filter(
            Favourite.user_id == user_id, 
            Favourite.property_id == property_id
        ).first() is not None

    @staticmethod
    def add(db: Session, user_id: int, property_id: int) -> Favourite:
        existing = db.query(Favourite).filter(
            Favourite.user_id == user_id, 
            Favourite.property_id == property_id
        ).first()
        if existing:
            return existing
        fav = Favourite(user_id=user_id, property_id=property_id)
        db.add(fav)
        db.commit()
        db.refresh(fav)
        return fav

    @staticmethod
    def remove(db: Session, user_id: int, property_id: int) -> bool:
        fav = db.query(Favourite).filter(
            Favourite.user_id == user_id, 
            Favourite.property_id == property_id
        ).first()
        if fav:
            db.delete(fav)
            db.commit()
            return True
        return False
