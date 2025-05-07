from typing import Optional
from app.models.user import User
from app.core.database import db

class UserRepository:
    @staticmethod
    def create(email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        return User.query.get(user_id)

    @staticmethod
    def update(user: User) -> User:
        db.session.commit()
        return user 