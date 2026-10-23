from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.entities import User
from backend.app.schemas.all_schemas import UserCreate, UserUpdate
from backend.app.core.security import get_password_hash

class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        user = User(
            name=user_in.name,
            email=user_in.email.lower().strip(),
            password_hash=get_password_hash(user_in.password),
            role=user_in.role,
            preferred_budget=user_in.preferred_budget,
            preferred_amenities=user_in.preferred_amenities,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: User, user_in: UserUpdate) -> User:
        if user_in.name is not None:
            user.name = user_in.name
        if user_in.preferred_budget is not None:
            user.preferred_budget = user_in.preferred_budget
        if user_in.preferred_amenities is not None:
            user.preferred_amenities = user_in.preferred_amenities
        db.commit()
        db.refresh(user)
        return user
